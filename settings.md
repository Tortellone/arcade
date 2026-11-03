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

SPRITE name:CAPITANO, x:206.0, y:456.0
SPRITE name:PORTAL, x:50.0, y:900.0, goto:2

PIATTAFORMA x:967, y:191, width:1920.0, height:50.0, color:BLUE
PIATTAFORMA x:198.0, y:402.0, width:200.0, height:20.0, color:GRAY
PIATTAFORMA x:1000.0, y:350.0, width:200.0, height:20.0, color:GRAY
PIATTAFORMA x:1300.0, y:450.0, width:200.0, height:20.0, color:GRAY
PIATTAFORMA x:1000.0, y:550.0, width:200.0, height:20.0, color:GRAY
PIATTAFORMA x:700.0, y:650.0, width:200.0, height:20.0, color:GRAY
PIATTAFORMA x:400.0, y:750.0, width:200.0, height:20.0, color:GRAY
PIATTAFORMA x:100.0, y:850.0, width:200.0, height:20.0, color:GRAY
PIATTAFORMA x:109.0, y:846.0, width:200.0, height:20.0, color:RED
PIATTAFORMA x:1659.3818488835939, y:924.5008492710934, width:200.0, height:20.0, color:RED
PIATTAFORMA x:990.0, y:754.0, width:200.0, height:20.0, color:RED
PIATTAFORMA x:1310.0, y:825.0, width:200.0, height:20.0, color:RED
PIATTAFORMA x:1946.6639959742186, y:1020.2615649679684, width:200.0, height:20.0, color:RED
PIATTAFORMA x:685.3027593354296, y:1110.2097845349222, width:200.0, height:20.0, color:RED
PIATTAFORMA x:2305.7666798374994, y:1131.982399947656, width:200.0, height:20.0, color:RED
PIATTAFORMA x:2619.6490257328123, y:1235.723175285937, width:200.0, height:20.0, color:RED
PIATTAFORMA x:2925.5513119867182, y:1336.8039307437496, width:200.0, height:20.0, color:RED
PIATTAFORMA x:2694.1295823859373, y:1469.804924767187, width:200.0, height:20.0, color:RED
PIATTAFORMA x:2356.307057566406, y:1530.9853820179683, width:200.0, height:20.0, color:RED
PIATTAFORMA x:2077.0049701171874, y:1589.5058193882808, width:200.0, height:20.0, color:RED
PIATTAFORMA x:1160.688943324877, y:2163.650523600602, width:200.0, height:20.0, color:RED
PIATTAFORMA x:2838.715934570679, y:570.0525633608779, width:200.0, height:20.0, color:RED
PIATTAFORMA x:2515.0713157140467, y:890.1793059255906, width:200.0, height:20.0, color:RED
PIATTAFORMA x:572.0, y:290.0, width:200.0, height:20.0, color:RED

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

SPRITE name:CAPITANO, x:50.0, y:250.0
SPRITE name:UFO, x:2000.0, y:880.0
SPRITE name:PORTAL, x:1860.0, y:250.0, goto:3


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

SPRITE name:CAPITANO, x:50.0, y:250.0
SPRITE name:UFO, x:2000.0, y:880.0
SPRITE name:PORTAL, x:1860.0, y:250.0, goto:4


## level
id=4
lenght: 1920
height: 3000
backgroundtype: image
backgroundimage: images\parallax_forest_1.png

SPRITE name:CAPITANO, x:50.0, y:250.0
SPRITE name:UFO, x:960.0, y:880.0

