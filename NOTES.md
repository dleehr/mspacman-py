# Notes

Just dev notes as I build this up - things to think about when going back to asm.

## 2023-01-16

Already surpassed what I have in 65816 version. Have the level map drawn as a background, and then the player sprite on top of that. It's a lot easier to work and refactor in Python as I'm learning how this should work.

I greatly improved the wall detection. One thing I'm not even sure is necessary is the checking alignment for off-axis movement, but it's a fast check.

 Now have dot-eating working. It changes the underlying wall tile index to 0 (just black) and prints a point value to the console. I need to update the score there and draw the score.

 But now what I'm thinking about is how to animate the 4 blinking dots. I could either replace the tile with a different one with the same score, or I could cycle the palette color for that. I bet that back in the day they cycled the palette color.

 Another thought - storing score characters. I didn't do these in the SNES version yet. But they'll definitely be loaded as tile maps. Maybe this just goes as more stuff in `walls.chr`.

## 2023-01-17

Curious if there was any info on how the ghosts move, and yes -- yes there is. A couple interesting things break my assumptions, via [The Pac-Man Dossier](https://pacman.holenet.info).

1. Movement around corners doesn't work the way I thought. Rounding a corner will actually cut a few diagonal pixels if you change direction early: [Chapter 2: Cornering](https://pacman.holenet.info/#CH2_Cornering).
2. Tapping the direction way in advance isn't enough to change it. Looks like it only starts to register maybe as you approach the tile. Maybe it's up to 4 pixels away - so half a tile - tested in MAME.
3. Speed varies and pac-man slows down when eating a dot: [Chapter 2: Speed](https://pacman.holenet.info/#CH2_Speed). I thought the dots slowed you down but haven't implemented that. Need to check these against MAME, not sure it's the same on Ms. Pac-Man as described for Pac-Man.

Now the score drawing is working. I have the surfaces in a list so each digit indexes its glyph. Then in python, I modulo 10, divide by 10, and repeat until 0. Can't really do that on SNES since I can't divide easily. But it looks like storing the scores can be done differently - either by manually handling the carry at 10 (see https://taywee.github.io/NerdyNights/nerdynights/numbers.html) or using BCD modes.

## 2023-01-19

Animations. Looked like only top right and bottom right tiles actually change but that's not true. The back of the face does change a tiny bit - not much but it's yellow. Transcribed the fully-open sprite, next need to do the fully closed and cycle the animation when moving. Then comes flipping and vertical.

