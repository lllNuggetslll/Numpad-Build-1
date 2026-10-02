function _top_case_walls_extrude_6_6_outline_fn(){
    return new CSG.Path2D([[88.8,-109.5],[88.8,4.5]]).appendArc([90.5,6.2],{"radius":1.7,"clockwise":true,"large":false}).appendPoint([166.5,6.2]).appendArc([168.2,4.5],{"radius":1.7,"clockwise":true,"large":false}).appendPoint([168.2,-109.5]).appendArc([166.5,-111.2],{"radius":1.7,"clockwise":true,"large":false}).appendPoint([90.5,-111.2]).appendArc([88.8,-109.5],{"radius":1.7,"clockwise":true,"large":false}).close().innerToCAG()
.subtract(
    new CSG.Path2D([[90,-109.5],[90,4.5]]).appendArc([90.5,5],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([166.5,5]).appendArc([167,4.5],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([167,-109.5]).appendArc([166.5,-110],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([90.5,-110]).appendArc([90,-109.5],{"radius":0.5,"clockwise":true,"large":false}).close().innerToCAG()
).extrude({ offset: [0, 0, 6.6] });
}


function top_case_inner_plate_extrude__1_6_outline_fn(){
    return new CSG.Path2D([[90,-109.5],[90,4.5]]).appendArc([90.5,5],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([166.5,5]).appendArc([167,4.5],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([167,-109.5]).appendArc([166.5,-110],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([90.5,-110]).appendArc([90,-109.5],{"radius":0.5,"clockwise":true,"large":false}).close().innerToCAG()
.subtract(
    new CSG.Path2D([[150,-12],[164,-12]]).appendPoint([164,2]).appendPoint([150,2]).appendPoint([150,-12]).close().innerToCAG()
.union(
    new CSG.Path2D([[150,-31],[164,-31]]).appendPoint([164,-17]).appendPoint([150,-17]).appendPoint([150,-31]).close().innerToCAG()
).union(
    new CSG.Path2D([[150,-59.5],[164,-59.5]]).appendPoint([164,-45.5]).appendPoint([150,-45.5]).appendPoint([150,-59.5]).close().innerToCAG()
).union(
    new CSG.Path2D([[150,-97.5],[164,-97.5]]).appendPoint([164,-83.5]).appendPoint([150,-83.5]).appendPoint([150,-97.5]).close().innerToCAG()
).union(
    new CSG.Path2D([[131,-12],[145,-12]]).appendPoint([145,2]).appendPoint([131,2]).appendPoint([131,-12]).close().innerToCAG()
).union(
    new CSG.Path2D([[131,-31],[145,-31]]).appendPoint([145,-17]).appendPoint([131,-17]).appendPoint([131,-31]).close().innerToCAG()
).union(
    new CSG.Path2D([[131,-50],[145,-50]]).appendPoint([145,-36]).appendPoint([131,-36]).appendPoint([131,-50]).close().innerToCAG()
).union(
    new CSG.Path2D([[131,-69],[145,-69]]).appendPoint([145,-55]).appendPoint([131,-55]).appendPoint([131,-69]).close().innerToCAG()
).union(
    new CSG.Path2D([[131,-88],[145,-88]]).appendPoint([145,-74]).appendPoint([131,-74]).appendPoint([131,-88]).close().innerToCAG()
).union(
    new CSG.Path2D([[131,-107],[145,-107]]).appendPoint([145,-93]).appendPoint([131,-93]).appendPoint([131,-107]).close().innerToCAG()
).union(
    new CSG.Path2D([[112,-12],[126,-12]]).appendPoint([126,2]).appendPoint([112,2]).appendPoint([112,-12]).close().innerToCAG()
).union(
    new CSG.Path2D([[112,-31],[126,-31]]).appendPoint([126,-17]).appendPoint([112,-17]).appendPoint([112,-31]).close().innerToCAG()
).union(
    new CSG.Path2D([[112,-50],[126,-50]]).appendPoint([126,-36]).appendPoint([112,-36]).appendPoint([112,-50]).close().innerToCAG()
).union(
    new CSG.Path2D([[112,-69],[126,-69]]).appendPoint([126,-55]).appendPoint([112,-55]).appendPoint([112,-69]).close().innerToCAG()
).union(
    new CSG.Path2D([[112,-88],[126,-88]]).appendPoint([126,-74]).appendPoint([112,-74]).appendPoint([112,-88]).close().innerToCAG()
).union(
    new CSG.Path2D([[93,-12],[107,-12]]).appendPoint([107,2]).appendPoint([93,2]).appendPoint([93,-12]).close().innerToCAG()
).union(
    new CSG.Path2D([[93,-31],[107,-31]]).appendPoint([107,-17]).appendPoint([93,-17]).appendPoint([93,-31]).close().innerToCAG()
).union(
    new CSG.Path2D([[93,-50],[107,-50]]).appendPoint([107,-36]).appendPoint([93,-36]).appendPoint([93,-50]).close().innerToCAG()
).union(
    new CSG.Path2D([[93,-69],[107,-69]]).appendPoint([107,-55]).appendPoint([93,-55]).appendPoint([93,-69]).close().innerToCAG()
).union(
    new CSG.Path2D([[93,-88],[107,-88]]).appendPoint([107,-74]).appendPoint([93,-74]).appendPoint([93,-88]).close().innerToCAG()
).union(
    new CSG.Path2D([[102.5,-107],[116.5,-107]]).appendPoint([116.5,-93]).appendPoint([102.5,-93]).appendPoint([102.5,-107]).close().innerToCAG()
)).extrude({ offset: [0, 0, -1.6] });
}




                function case_top_case_fn() {
                    

                // creating part 0 of case case_top
                let case_top__part_0 = _top_case_walls_extrude_6_6_outline_fn();

                // make sure that rotations are relative
                let case_top__part_0_bounds = case_top__part_0.getBounds();
                let case_top__part_0_x = case_top__part_0_bounds[0].x + (case_top__part_0_bounds[1].x - case_top__part_0_bounds[0].x) / 2
                let case_top__part_0_y = case_top__part_0_bounds[0].y + (case_top__part_0_bounds[1].y - case_top__part_0_bounds[0].y) / 2
                case_top__part_0 = translate([-case_top__part_0_x, -case_top__part_0_y, 0], case_top__part_0);
                case_top__part_0 = rotate([0,0,0], case_top__part_0);
                case_top__part_0 = translate([case_top__part_0_x, case_top__part_0_y, 0], case_top__part_0);

                case_top__part_0 = translate([0,0,0], case_top__part_0);
                let result = case_top__part_0;
                
            

                // creating part 1 of case case_top
                let case_top__part_1 = top_case_inner_plate_extrude__1_6_outline_fn();

                // make sure that rotations are relative
                let case_top__part_1_bounds = case_top__part_1.getBounds();
                let case_top__part_1_x = case_top__part_1_bounds[0].x + (case_top__part_1_bounds[1].x - case_top__part_1_bounds[0].x) / 2
                let case_top__part_1_y = case_top__part_1_bounds[0].y + (case_top__part_1_bounds[1].y - case_top__part_1_bounds[0].y) / 2
                case_top__part_1 = translate([-case_top__part_1_x, -case_top__part_1_y, 0], case_top__part_1);
                case_top__part_1 = rotate([0,0,0], case_top__part_1);
                case_top__part_1 = translate([case_top__part_1_x, case_top__part_1_y, 0], case_top__part_1);

                case_top__part_1 = translate([0,0,0], case_top__part_1);
                result = result.union(case_top__part_1);
                
            
                    return result;
                }
            
            
        
            function main() {
                return case_top_case_fn();
            }

        