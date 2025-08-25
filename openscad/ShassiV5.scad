

include <Round-Anything-1.0.4/polyround.scad>

use <obiscad/bevel.scad>
use <obiscad/attach.scad>

K=2.5;


module sector(radius, angles, fn = 24) {
    r = radius / cos(180 / fn);
    step = -360 / fn;

    points = concat([[0, 0]],
        [for(a = [angles[0] : step : angles[1] - 360]) 
            [r * cos(a), r * sin(a)]
        ],
        [[r * cos(angles[1]), r * sin(angles[1])]]
    );

    difference() {
        circle(radius, $fn = fn);
        polygon(points);
    }
}


module iso_triangle(side,tall,corner_radius,triangle_height){
    
    translate([0,corner_radius,0]){
    hull(){
    translate([side/2-corner_radius,0])cylinder(r=corner_radius,h=triangle_height, center=true);   
    translate([-side/2+corner_radius,0])cylinder(r=corner_radius,h=triangle_height, center=true);
    translate([0,tall-corner_radius*2,0])cylinder(r=corner_radius,h=triangle_height, center=true);    
        }
}
}

module inv_triangle(side,height,k=K) {
    difference()
    {
     translate([-side*0.4        ,0,0]) cube([k*side,k*side,height],center=true); //plate
     cylinder(r=side, h=height*1.1, $fn=3,center=true); //triangle
    }
}


// from candle exaMPLE
module make_ring_of(radius, count){
    for (a = [0 : count - 1]) {
        angle = a * 360 / count;
        translate(radius * [cos(angle), -sin(angle), 0])
                children();
    }
}




module tube(inner,outer, height) {
    translate([0,0,-height+1.5])
    difference()
    {
     cylinder(r=outer, h=height*1, $fn=50); //outer
     cylinder(r=inner, h=height*1, $fn=50); //inner
    }
}

module inv_tr_cil(side,r_cir, height,k=K) {
        union ()
           inv_triangle(side,height,k);
           tube(r_cir,r_cir+5,height*2);
           translate([-side*0.4          ,0,-height]) cube([k*side,k*side,height],center=true);
    
}
    

module inv_tr_cil_cable(side,r_cir, height,c1,c2) {
    difference () {
        difference () {   
               {
               difference () {
               inv_tr_cil(side,r_cir, height); //plate-rounded triangle
               translate([-r_cir*0.86,0,0])  cube([c2,c1,4*height], center=true); // hole for cable
               }
               }
                //Making holes in candle holder
                color ("red") make_ring_of(17/2, 3){ // 17 small
                    cylinder(h=10,r=2.6/2, center=true, $fn=50);
                }
               
           }
           
        // minus  
            {       
            translate([0,0,-10])
            linear_extrude([10]) {
                    polygon(points=[[side-2.5,side-8],[side-0.3,side*2],[side-25,side+10]]);
                    polygon(points=[[side-2.5,-(side-8)],[side-0.3,-side*2],[side-25,-(side+10)]]);
                   }
            }
         }
//-- Parts parameters




//-- Define the connectors
connByZ=-side-8;
connByY1=side-1;
connByY2=-side+1;
connByX=-side/4;
connFat=side-8;
connSize=side+2*height+2;                  
ec1 = [ [connByZ, connByY1, connByX], [0,1,0],  0];
ec2 = [ [connByZ, connByY2, connByX], [0,1,0],  0];
en1 = [ ec1[0],                    [-0,0,0], 0];
en2 = [ ec2[0],                    [0,0,0], 0];
bconcave_corner_attach(ec1,en1,l=connFat,cr=connSize,cres=20);         
bconcave_corner_attach(ec2,en2,l=connFat,cr=connSize,cres=20);                  
         
}

module make_strong_angles(dx1,dy1,dz1){
    for (N = [0 : 3]) {
        if (N==0) {
          translate([0,0,dz1])  
            rotate([-90,-90,0])  children();
        } else if (N==1) {
           translate([dx1,0,dz1]) 
             rotate([90,-90,0])   children();
        } else if (N==2) { 
           translate([0,dy1,dz1])  
            rotate([-90,-90,0])   children();
        } else if (N==3) {
           translate([dx1,dy1,dz1]) 
            rotate([90,270,0])  children();
        }
                
    }
}


module right_4triangle(height,W=5,dx1 ,dy1 ,dz1 ){
    triangle_points = [
    [0, 0], // Vertex 1 (origin)
    [W, 0], // Vertex 2 (horizontal side)
    [0, W]  // Vertex 3 (vertical side)
    ];
    //imake_strong_angles(100,200) linear_extrude (height = height) polygon(points = triangle_points);
    //make_strong_angles(dx1=dx1,dy1=dy1,dz1=dz1) linear_extrude (height = height) polygon(points = triangle_points);
    make_strong_angles(dx1=dx1,dy1=dy1,dz1=dz1) linear_extrude (height = height, center=true) polygon(points = triangle_points) ;
}


module chassis_plate(side,r_cir, height,L,W, net_tall,net_height,c1,c2) {
    deltaUp=side*(K/2+0.4);    
    deltaW=side*(K/2); 
    deltaNetX= L/2-height/2   ;
    deltaNetY= W/2-side*(K/2)   ;
    deltaNetZ= -side*(K/2+0.4)   ;
    netTriH=W*(1+sin(30));
    batL=69;
    batD1=16;
    batD2=batD1+23;
    
    batR=4/2;
    switchR=22/2; //21 origin
    switchD1=batD2+35;
    switchD2=36;
    panL=46;
    panD1=95; //80
    panD2=panD1+86;
    
    drills=[[-height/2+L/2-batL/2,-deltaW+batD1, 0,batR],
            [-height/2+L/2+batL/2,-deltaW+batD1,0,batR],
            [-height/2+L/2-batL/2,-deltaW+batD2, 0,batR],
            [-height/2+L/2+batL/2,-deltaW+batD2,0,batR],
    
            [-height/2+L/2-panL/2,-deltaW+panD1, 0,batR],
            [-height/2+L/2+panL/2,-deltaW+panD1,0,batR],
            [-height/2+L/2-panL/2,-deltaW+panD2, 0,batR],
            [-height/2+L/2+panL/2,-deltaW+panD2,0,batR],
            
            [-height/2+L/2,-deltaW+(panD1+batD2+10)/2,0,2.5*batR],
            
            [-height/2+L/2+switchD2,-deltaW+switchD1,0,switchR]
            
    
    ];
    //echo (len(drills));
    difference () {
        intersection () {
        
            union () {        
                translate([-height/2,-deltaW, -deltaUp]) cube([L,W,height])    ; //plate
                translate([deltaNetX,W-L-5, -deltaUp])    linear_extrude(height) sector(radius=L, angles=[60,120], fn=24); // rear bumper
                translate([deltaNetX,W-L+10, -deltaUp])   linear_extrude(height) sector(radius=L, angles=[240,300], fn=24);// front bumper
                
                
                translate([height*1.5,0,0]) right_4triangle(height=side*(4*K),W=height*2.5,dx1=L-height*4,dy1=W-2*side*K/2,dz1=-2*side+3*height);  //wheel corner angle

             translate([deltaNetX,deltaNetY,deltaNetZ ]) rotate ([90,0,150])  iso_triangle(side=net_height,tall=net_tall,corner_radius=1,triangle_height=netTriH);
             translate([deltaNetX,deltaNetY,deltaNetZ ]) rotate ([90,0,30])  iso_triangle(side=net_height,tall=net_tall,corner_radius=1,triangle_height=netTriH);
             translate([deltaNetX,deltaNetY,deltaNetZ ]) rotate ([90,0,90])  iso_triangle(side=net_height,tall=net_tall,corner_radius=1,triangle_height=L);


            }; //union 
            //intersection with
            union () {
            translate([-height/2,-deltaW, -net_tall-deltaUp-12])   cube([L,W, 2*height+net_tall*2])    ; //plate grow ap and down
            translate([deltaNetX,W-L-5, -net_tall-deltaUp-12])    linear_extrude(2*height+net_tall*2)  
                sector(radius=L, angles=[60,120], fn=24); 

            translate([deltaNetX,W-L+10, -net_tall-deltaUp-12])    linear_extrude(2*height+net_tall*2)  
                 sector(radius=L, angles=[240,300], fn=24); 
            
            } // union 
        
        }; //intersection end
        union () {   //drills
          for (ii = [0 : len(drills)-1]) {
            translate([drills[ii][0], drills[ii][1], drills[ii][2]]) cylinder(r=drills[ii][3],h=100, center=true, $fn=50); 
          }
      }
    }
    
}


module  tof_holder(side, L,W ,height, Lh=10,Wh=14,Hh=3) {
    deltaNetZ= -height+Lh-side*(K/2+0.4)   ;
    tofR=3/2;
    tofSens=3.0;
    WSens=4.4;
    color("red") 
    difference()
    
    {
translate([L/2,-0.3*L,deltaNetZ]) cube([Wh+5,Hh,Lh+2], center=true) ;
        
translate([L/2-(Wh)/2,-0.2*L,deltaNetZ+2])        
       rotate([90,0,0]) 
        {
            cylinder(r=tofR,h=100, center=true, $fn=10); 
            translate ([Wh,0,0]) cylinder(r=tofR,h=100, center=true, $fn=10); 
            translate ([WSens/2+tofSens/2+1.1,0]) hull() {
            cylinder(r=tofSens,h=100, center=true, $fn=10); 
            translate ([WSens,0,0]) cylinder(r=tofSens,h=100, center=true, $fn=10); 
}
        }    
    }
}

module chassi(side,r_cir, height,c1=14,c2=8, L=100,W=200,net_tall,net_height) {
    deltaW=side*(K/2);    
union () {    
    translate([0,0,0 ])  rotate([0,-90,0]) inv_tr_cil_cable(side=side,r_cir=r_cir, height=height,c1=c1,c2=c2); //front left wheel
    translate([0,W-2*deltaW, 0])  rotate([0,-90,0]) inv_tr_cil_cable(side=side,r_cir=r_cir, height=height,c1=c1,c2=c2); //rear left wheel
    mirror([1,0,0]) translate([-L+height,0, 0])           rotate([0,-90,0]) inv_tr_cil_cable(side=side,r_cir=r_cir, height=height,c1=c1,c2=c2); //front right wheel
    mirror([1,0,0]) translate([-L+height,W-2*deltaW, 0])  rotate([0,-90,0]) inv_tr_cil_cable(side=side,r_cir=r_cir, height=height,c1=c1,c2=c2); //rear  right wheel
    chassis_plate(side=side, height=height, L=L,W=W,net_tall=net_tall,net_height=net_height); // plate
    tof_holder(side=side,height=height, L=L,W=W ,Lh=13,Wh=14,Hh=3);
    
}    
}

tC1=14;
tC2=2;
//tSide=17.5;
tSide=18;
tCirD=25;
tH=3;
tL=120;
tW=190;

//chassi(side=tSide,r_cir=tCirD/2, height=tH, L=tL,W=tW ,net_tall=8, net_height=30,c1=14,c2=8);
chassi(side=tSide,r_cir=tCirD/2, height=tH, L=tL,W=tW ,net_tall=12, net_height=30,c1=14,c2=8);





