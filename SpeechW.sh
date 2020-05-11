#!/bin/bash
#################################
# Speech Script by Dan Fountain #
#      TalkToDanF@gmail.com     #
#################################
 
 
INPUT=$*
STRINGNUM=0
NOWDATE=`date +%Y-%m-%d_%H-%M-%S_%3N`
USR_AGT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
 
ary=($INPUT)
LANG="EN-gb"

echo "---------------------------"
echo "Speech Script by Dan Fountain"
echo "TalkToDanF@gmail.com"
echo "---------------------------"
for key in "${!ary[@]}" 
  do
    SHORTTMP[$STRINGNUM]="${SHORTTMP[$STRINGNUM]} ${ary[$key]}"
    LENGTH=$(echo ${#SHORTTMP[$STRINGNUM]})
    echo "word:$key, ${ary[$key]}"
    echo "adding to: $STRINGNUM"
    if [[ "$LENGTH" -lt "100" ]]; then
      #echo starting new line
      SHORT[$STRINGNUM]=${SHORTTMP[$STRINGNUM]}
    else
      STRINGNUM=$(($STRINGNUM+1))
      SHORTTMP[$STRINGNUM]="${ary[$key]}"
      SHORT[$STRINGNUM]="${ary[$key]}"
    fi
done
 
for key in "${!SHORT[@]}"
  do
    echo "line: $key is: ${SHORT[$key]}"
 
    echo "Playing line: $(($key+1)) of $(($STRINGNUM+1))"
    NEXTURL=$(echo ${SHORT[$key]} | xxd -plain | tr -d '\n' | sed 's/\(..\)/%\1/g')
    NEXTREQ="http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q=$NEXTURL&tl=$LANG"
    NEXTFILENAME="${NOWDATE}_googtts.mp3"
    wget -U "$USR_AGT" "$NEXTREQ" -O - >> $NEXTFILENAME
    echo $NEXTREQ >> GT_tts_requests.txt
    play -q "$NEXTFILENAME" pitch 500
done