# Sprites settings

## CAPITANO
walk.speed:5
run.speed:10
width:100
height:100

## UFO
speed:2
shoot.interval:2.0
bullet.speed: 5
width:96
height:96

## BULLET_PLASMA
speed:20
width:40
height:20

## BULLET_ENERGY
width:40
height:40

# Levels settings

## level
id=1
lenght: 19200
height: 3000
backgroundtype: parallax
parallaximage 1: images\parallax_forest_1.png
parallaximage 2: images\parallax_forest_2.png
parallaximage 3: images\parallax_forest_3.png
parallaximage 4: images\parallax_forest_4.png
parallaximage 5: images\parallax_forest_5.png
parallaximage 6: images\parallax_forest_6.png
parallaximage 7: images\parallax_forest_7.png

SPRITE name:CAPITANO, x:50, y:285
SPRITE name:UFO, x:1900, y:400
SPRITE name:UFO, x:1400, y:600
SPRITE name:PORTAL, x:50, y:900, goto:2

PIATTAFORMA x:960, y:285, width:1920, height:50, color:TRANSPARENT
PIATTAFORMA x:200, y:350, width:200, height:20, color:BLU
PIATTAFORMA x:1000, y:350, width:200, height:20, color:BLU
PIATTAFORMA x:1300, y:450, width:200, height:20, color:BLU
PIATTAFORMA x:1000, y:550, width:200, height:20, color:BLU
PIATTAFORMA x:700, y:650, width:200, height:20, color:BLU
PIATTAFORMA x:400, y:750, width:200, height:20, color:BLU
PIATTAFORMA x:100, y:850, width:200, height:20, color:BLU


## level
id=2
lenght: 1920
height: 3000
backgroundtype: parallax
parallaximage 1: images\city_1.png
parallaximage 2: images\city_2.png
parallaximage 3: images\city_3.png
parallaximage 4: images\city_4.png
parallaximage 5: images\city_5.png
parallaximage 6: images\city_6.png
parallaximage 7: images\city_7.png
parallaximage 8: images\city_8.png

SPRITE name:CAPITANO, x:50, y:250
SPRITE name:UFO, x:2000, y:880
SPRITE name:PORTAL, x:1860, y:250, goto:3

## level
id=3
lenght: 1920
height: 3000
backgroundtype: parallax
parallaximage 1: images\mountains_1.png
parallaximage 2: images\mountains_2.png
parallaximage 3: images\mountains_3.png
parallaximage 4: images\mountains_4.png
parallaximage 5: images\mountains_5.png

SPRITE name:CAPITANO, x:50, y:250
SPRITE name:UFO, x:2000, y:880
SPRITE name:PORTAL, x:1860, y:250, goto:4

## level
id=4
lenght: 1920
height: 3000
backgroundtype: image
backgroundimage: images\parallax_forest_1.png

SPRITE name:CAPITANO, x:50, y:250
SPRITE name:UFO, x:960, y:880


