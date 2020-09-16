///////////////////////////////////////////////////////////////////////////////
// Copyright (c) 1995/2015 Xilinx, Inc.
// All Right Reserved.
///////////////////////////////////////////////////////////////////////////////
//   ____  ____
//  /   /\/   /
// /___/  \  /    Vendor : Xilinx
// \   \   \/     Version : 2015.4
//  \   \         Description : Xilinx Formal Library Component
//  /   /                  Bi-Directional Buffer
// /___/   /\     Filename : IOBUF_INTERMDISABLE.v
// \   \  /  \
//  \___\/\___\
//
///////////////////////////////////////////////////////////////////////////////
// Revision:
//    04/20/11 - Initial version.
//    10/20/14 - Removed b'x support (CR 817718).
// End Revision
///////////////////////////////////////////////////////////////////////////////

`timescale  1 ps / 1 ps

`celldefine

module IOBUF_INTERMDISABLE (O, IO, I, IBUFDISABLE, INTERMDISABLE, T);

    parameter integer DRIVE = 12;
    parameter IBUF_LOW_PWR = "TRUE";
    parameter IOSTANDARD = "DEFAULT";
    parameter SIM_DEVICE = "7SERIES";
    parameter SLEW = "SLOW";
    parameter USE_IBUFDISABLE = "TRUE";
`ifdef XIL_TIMING
    parameter LOC = "UNPLACED";
`endif // `ifdef XIL_TIMING

    output O;
    inout  IO;
    input  I;
    input  IBUFDISABLE;
    input  INTERMDISABLE;
    input  T;

    wire ts;
    wire T_OR_IBUFDISABLE;


    or O1 (ts,  T);
    bufif0 T1 (IO, I, ts);

//    buf B1 (O, IO);

    generate
       case (USE_IBUFDISABLE)
          "TRUE" :  begin
                       assign T_OR_IBUFDISABLE = ~T || IBUFDISABLE;
                       assign O = (T_OR_IBUFDISABLE == 1'b1) ? 1'b1 : (T_OR_IBUFDISABLE == 1'b0) ? IO : 1'b0;
                    end
          "FALSE" : begin
                        assign O = IO;
                    end
       endcase
    endgenerate

endmodule

`endcelldefine
