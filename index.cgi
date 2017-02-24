#!/bin/sh
#
# CGI/SHell MediaBox using HTML5 features. Coded with lightness and 
# elegance in mind.
#
# Copyright (C) 2017 SliTaz GNU/Linux - BSD License
#
. /usr/lib/slitaz/httphelper.sh
header

#
# Internal variables
#
version="beta"
cache="$PWD/cache"
script="$SCRIPT_NAME"

# Set $home - Cache user ID and source configs
if [ "$(GET home)" ]; then
	echo $(GET home) > ${cache}/home
	rm -f ${cache}/audio ${cache}/videos
fi
home=$(cat $cache/home)
config="$home/.config/mediabox"
if [ -f "${config}/mediabox.conf" ]; then
	. ${config}/mediabox.conf
else
	gettext "Missing config file:"; echo " $config"; exit 1
fi

# i18n
export LANG=${LOCALE} LC_ALL=${LOCALE}
. /usr/bin/gettext.sh
export TEXTDOMAIN='mediabox'

#
# Functions
#

# Usage: html_header "Page Title"
html_header() {
	cat lib/header.html | sed s"/%TITLE%/$1/"
	cat << EOT
<header>
	<h1>$1</h1>
EOT
}

html_footer() {
	cat << EOT
<footer>
	&hearts;
</footer>
</body>
</html>
EOT
}

# Header navigation
nav_menu() {
	cat << EOT
	<nav>
		<a href="$script">$(gettext "Home")</a>
		<a href="$script?music">$(gettext "Music")</a>
		<a href="$script?videos">$(gettext "Videos")</a>
		<a href="$script?playlists">$(gettext "Playlists")</a>
		<a href="$script?radio">$(gettext "Radio")</a> 
	</nav>
</header>
EOT
}

# Page navigation
nav_page() {
	cat << EOT
</header>
<div id="home">
	<nav >
		<a href="$script?music">$(gettext "Music")</a>
		<a href="$script?videos">$(gettext "Videos")</a>
		<a href="$script?playlists">$(gettext "Playlists")</a>
		<a href="$script?radio">$(gettext "Radio")</a>
		<a href="$script?settings">$(gettext "Settings")</a>
	</nav>
</div>
EOT
}

# Find and list audio/videos files.
find_audio() {
	[ ! -f "${cache}/audio" ] && find "${MUSIC}" \
		-regex '.*\.\(mp3\|ogg\|wav\)' > ${cache}/audio
	cat ${cache}/audio
}
find_videos() {
	find "${VIDEOS}" -regex '.*\.\(mp4\|ogv\|avi\)' > ${cache}/videos
	cat ${cache}/videos
}

list_audio() {
	count="$(wc -l ${cache}/audio | cut -d " " -f 1)"
	echo "<ul id='audio-list'>"
	cat << EOT
	<li><span>&#9835 &#9835 &#9835  $count $(gettext "Tracks found")</span></li>
EOT
	find_audio | while read a
	do
		filename="$(basename "${a}")"
		echo "	<li><a href='$script?music&amp;play=${a}'>${filename%.*}</a></li>"
	done
	echo "</ul>" 
}

list_videos() {
	count="$(wc -l ${cache}/videos | cut -d " " -f 1)"
	cat << EOT
<ul id='videos-list'>
	<li><span>$count $(gettext "Videos found")</span></li>
EOT
	find_videos | while read v
	do
		filename="$(basename "${v}")"
		echo "	<li><a href='$script?videos&amp;play=${v}'>${filename%.*}</a></li>"
	done
	echo "</ul>" 
}

list_radio() {
	if [ ! -f "$config/radio.list" ]; then
		cp lib/radio.list ${config} && chmod 0666 ${config}/radio.list
	fi
	echo "<ul id='radio-list'>"
	IFS="|"
	cat ${config}/radio.list | while read url info
	do
		[ "$info" ] || info="N/A"
		cat << EOT
	<li><a href='$script?radio&amp;play=${url}&info=$info'>${url#http://}<span>$info</span></a></li>
EOT
	done
	unset IFS info
	echo "</ul>" 
}

list_playlists() {
	echo "<ul id='radio-list'>"
	IFS="|"
	cat ${config}/playlists.list | while read file info
	do
		[ "$info" ] || info="N/A"
		cat << EOT
	<li><a href='$script?playlists&amp;play=${file}&info=$info'>$info</a></li>
EOT
	done
	unset IFS info
	echo "</ul>" 
}

# HTML5 audio/video attributes: autoplay loop controls preload="auto"
#
# Usage: audio_player [/path/audio.ogg|http://url]
audio_player() {
	case "$1" in
		http://*)
			source="$1" title="$2" ;;
		*)
			filepath="$1"
			filename="$(basename "$1")"
			title="$(gettext "No track playing")"
			[ "$1" ] && title="${filename%.*}"	
			# We need to get file via http url
			source="cache/play/$filename"
			rm -rf ${cache}/play && mkdir ${cache}/play
			[ "$filename" ] && ln -s "$filepath" "$cache/play/$filename" ;;
	esac
	cat << EOT
<div id="audio-player">
	<div id="audio-title">$title</div>
	<audio controls autoplay="true" preload="auto">
		<source src="$source">
		<div>Your browser does not support audio</div>
	</audio>
</div>
EOT
}

playlist_player() {
	playlist="$1"
}

# Usage: video_player "/path/video.mp4"
video_player() {
	filepath="$1"
	filename="$(basename "$1")"
	title="$(gettext "No video playing")"
	[ "$1" ] && title="${filename%.*}"	
	# We need to get file via http url
	rm -rf ${cache}/play && mkdir ${cache}/play
	[ "$filename" ] && ln -s "$filepath" "$cache/play/$filename"
	cat << EOT
<div id="video-player">
	<video width="560px" height="315px" 
		controls autoplay="true" poster="images/poster.png">
		<source src="cache/play/$filename">
		<div>Unsupported video file format</div>
	</video>
	<div id="video-title">$title</div>
</div>
EOT
}

#
# Media Box Tools
#

case " $(GET) " in
	*\ music\ *)
		html_header "$(gettext "Music")"
		nav_menu
		audio_player "$(GET play)"
		list_audio
		html_footer ;;
	
	*\ videos\ *)
		html_header "$(gettext "Videos")"
		nav_menu
		video_player "$(GET play)"
		list_videos
		html_footer ;;
	
	*\ playlists\ *)
		html_header "$(gettext "Playlists")"
		nav_menu
		playlist_player "$(GET play)" "$(GET info)"
		list_playlists
		html_footer ;;
	
	*\ radio\ *)
		html_header "$(gettext "Radio")"
		nav_menu
		audio_player "$(GET play)" "$(GET info)"
		list_radio
		html_footer ;;
	
	*\ settings\ *) 
		html_header "$(gettext "Settings")"
		nav_menu
		cat << EOT
<div id="settings">
<pre>
Version     : $version
Cache       : $(du -sh $cache | cut -d "	" -f 1)
Language    : $LOCALE
Config      : $config
Music       : $MUSIC
Videos      : $VIDEOS
EOT
		echo -n "Tools       : "
		# Only small and light tools!
		for tool in mediainfo normalize sox
		do
			if [ -x "/usr/bin/$tool" ]; then
				echo -n "$tool "
			fi
		done
		cat << EOT


$(cat README)
</pre>
EOT
		# End of <div id="settings">
		echo "</div>"
		html_footer ;;
	
	*)
		# Home page
		html_header "MediaBox"
		nav_page
		html_footer ;;
esac && exit 0
