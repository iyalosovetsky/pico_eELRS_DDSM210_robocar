# ELRS car platform



 This project has code to control the car platform by express ELRS receiver like betafpv nano receiver and TX12 RC . 
 The car is a four wheel drive platform powered by 4 PWM controlled motors. The code implements CRSF protocol on Raspberry Pico W to send command and retrieve telemetry data (battery state). 


VIDEO [![Watch the video](https://img.youtube.com/vi/cAvKrcaPvDQ/default.jpg)](https://youtu.be/cAvKrcaPvDQ)

The parts 

| Part name                            |                                                         | Further info              | 
|-------------------------------------|-------------------------------------------------------------------|---------------------------|
|Raspberry Pi5                     |      [![Raspberry Pi5                      ](https://www.raspberrypi.com/documentation/computers/images/5.jpg?hash=b888dab3bb8bcb8dd4e0541c99238eec)](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html) | [Link](https://www.itbox.ua/ua/product/Promisloviy_PK_Raspberry_Pi_5_8GB_RPI5-8GB-p1015792/) |
|Raspberry Pico 2W                     |      [![Raspberry Pico 2 W                      ](https://www.raspberrypi.com/documentation/microcontrollers/images/pico2w-pinout.svg)](https://arduino.ua/prod8038-raspberry-pi-pico-2w) | [Link](https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf) |
|RadioMaster TX12 MKII ExpressLRS Edge TX   | [![RadioMaster TX12 MKII ExpressLRS Edge TX](https://brain.com.ua/static/images/prod_img/9/5/U0846495_big_1739048900.jpg)        ](https://brain.com.ua/ukr/Pult_upravlinnya_dlya_drona_RadioMaster_TX12_MKII_ExpressLPS_Edge_TX_HP01570032-M2-p1044984.html?utm_content=shopping&gad_source=1&gclid=Cj0KCQiAwtu9BhC8ARIsAI9JHaluyF0pBA9Hv_9k_8fUJQQ3mH0yfzvPo3ofY5IHeKnd9vogtm-17KQaAj6fEALw_wcB) | [Link](https://brain.com.ua/ukr/Pult_upravlinnya_dlya_drona_RadioMaster_TX12_MKII_ExpressLPS_Edge_TX_HP01570032-M2-p1044984.html?utm_content=shopping&gad_source=1&gclid=Cj0KCQiAwtu9BhC8ARIsAI9JHaluyF0pBA9Hv_9k_8fUJQQ3mH0yfzvPo3ofY5IHeKnd9vogtm-17KQaAj6fEALw_wcB) |
|Receiver BETAFPV NANO 2400           | [![Receiver BETAFPV NANO 2400](https://www.expresslrs.org/assets/images/betaFPVrx2400.png)](https://prom.ua/ua/p2130654195-priemnik-elrs-24ghz.html) | [Link](https://prom.ua/ua/p2130654195-priemnik-elrs-24ghz.html)       |
|DDSM210                         | [![DDSM210)](https://www.waveshare.com/media/catalog/product/cache/1/image/800x800/9df78eab33525d08d6e5fb8d27136e95/d/d/ddsm210-2_4.jpg) | [link](https://www.waveshare.com/wiki/DDSM210)       |
|Pan Tilt2, General General Robot Driver Board                         | [![Pan Tilt)](https://www.waveshare.com/media/catalog/product/cache/1/image/800x800/9df78eab33525d08d6e5fb8d27136e95/2/-/2-axis-pan-tilt-camera-module-1.jpg) | [link](https://www.waveshare.com/wiki/2-Axis_Pan-Tilt_Camera_Module)  
[general driver]([https://www.waveshare.com/wiki/2-Axis_Pan-Tilt_Camera_Module](https://www.waveshare.com/general-driver-for-robots.htm))   
|
|optical sensor                       | [![Time Of Flight TOF050C-VL6180X](https://diyshop.com.ua/image/cache/catalog/product/microcontroller/sensors/VL53L0X/TOF050C-VL6180X-400x400.jpg)](https://diyshop.com.ua/ua/vysokotochnyj-infrakrasnij-dalnomer-tof050c-vl6180?srsltid=AfmBOorClwI3dhHLDG-7Ixro-sT2cQ8p7tcU3HmgcwFo66yI-3CkeiL9) | [Link](https://diyshop.com.ua/ua/vysokotochnyj-infrakrasnij-dalnomer-tof050c-vl6180?srsltid=AfmBOorClwI3dhHLDG-7Ixro-sT2cQ8p7tcU3HmgcwFo66yI-3CkeiL9)       |
|3S charger  ip2326           | [![3S charger  ip2326](https://arduino.ua/products_pictures/large_aoc863_3.jpg)](https://arduino.ua/prod5917-modyl-zaryadybms-z-qc-dlya-3s-li-ion-type-c-ip2326) | [Link](https://arduino.ua/prod5917-modyl-zaryadybms-z-qc-dlya-3s-li-ion-type-c-ip2326)       |
|3x 18650 3000mAh           | [![3x 21700  5000mAh 30A](https://img4.itbox.ua/1600x1600/prod_img/4/U0885194_4big_1723288696.webp)](https://www.itbox.ua/ua/product/Akumulyator_JHY_Li-Ion_21700_5000mAh_36V_30A_INR21700-50SE-p999120/) | [link](https://www.itbox.ua/ua/product/Akumulyator_JHY_Li-Ion_21700_5000mAh_36V_30A_INR21700-50SE-p999120/)       |
|XL-7015  DC-DC step down buck converter         | [![2S charger and bms ip2326](https://images.prom.ua/5129390527_peretvoryuvachstabilizator-znizhuvalnij-xl7015.jpg)](https://e-to4ka.com.ua/ua/p2025663723-preobrazovatelstabilizator-ponizhayuschij-xl7015.html) | [Link](https://e-to4ka.com.ua/ua/p2025663723-preobrazovatelstabilizator-ponizhayuschij-xl7015.html)       |





see my project to control by bluetouth joystick  https://github.com/iyalosovetsky/robocar 

also  RC by CRSF protocol https://github.com/iyalosovetsky/pico_expressELRS_car/blob/main/README.md
