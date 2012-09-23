// Distance between Ultimaker mounting screws
seperation = 117;

// Thickness of mounting plate
thickness = 3;

// Width of mounting plate
width = 22;

// Radius of screw hole
hole = 1.75;

// Amount the plate can adjust
slide = 4;


module slot(r, thickness, freedom) {
    union() {
        for (y = [-freedom / 2, freedom / 2]) {
            translate([y, 0, 0])
            cylinder(h=thickness, r=r, center=true);
        }
        cube([freedom, r * 2, thickness], center=true);
    }
}


module plate() {
    difference() {
        difference() {
            slot(width / 2, thickness, seperation + (width / 4));
            cube([75, width * 2, thickness * 2], center=true);
        }
        for (y = [-seperation / 2, seperation / 2]) { 
            translate([y, 0, 0])
            slot(hole, thickness * 2, hole + slide);
        }
    }
}


ot = 4;

union() {
    translate([0, 0, thickness / 2])
    rotate(90, [0, 0, 1])
    plate();
    import("raspberrypiplate.stl");

    for (x = [-19.5, 19.5]) {
        for (y = [-32.5, 32.5]) {
            translate([x, y, ot / 2])
            cube([6, 6, ot], center=true);
        }
    }
}


