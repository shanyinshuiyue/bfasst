///////////////////////////////////////////////////////////////////////////////
// Copyright (c) 1995/2015 Xilinx, Inc.
// All Right Reserved.
///////////////////////////////////////////////////////////////////////////////
//   ____  ____
//  /   /\/   /
// /___/  \  /    Vendor : Xilinx
// \   \   \/     Version : 2015.4
//  \   \         Description : Xilinx Formal Library Component
//  /   /                  128x1 Static RAM with synchronous write capability
// /___/   /\     Filename : RAM128X1S.v
// \   \  /  \
//  \___\/\___\
//
///////////////////////////////////////////////////////////////////////////////
// Revision:
//    04/01/08 - Initial version.
//    08/30/13 - PR683925 - add invertible pin support.
// End Revision
///////////////////////////////////////////////////////////////////////////////

`timescale  1 ps / 1 ps

`celldefine

module RAM128X1S (O, A0, A1, A2, A3, A4, A5, A6, D, WCLK, WE);

    parameter [127:0] INIT = 128'h00000000000000000000000000000000;
    parameter [0:0] IS_WCLK_INVERTED = 1'b0;
 
`ifdef XIL_TIMING //Simprim
 
  parameter LOC = "UNPLACED";

`endif

    output O;

    input  A0, A1, A2, A3, A4, A5, A6, D, WCLK, WE;
    wire WCLK_in;

    assign WCLK_in = IS_WCLK_INVERTED ^ WCLK;

    FORMAL_INV INV_A4 (
      .I (A4),
      .O (A4_INV)
    );
    FORMAL_INV INV_A5 (
      .I (A5),
      .O (A5_INV)
    );
    FORMAL_INV INV_A6 (
      .I (A6),
      .O (A6_INV)
    );

    FORMAL_AND4 AND_WE_0 (
      .I0 (A4_INV),
      .I1 (A5_INV),
      .I2 (A6_INV),
      .I3 (WE),
      .O (WE_0)
    );
    FORMAL_AND4 AND_WE_1 (
      .I0 (A4),
      .I1 (A5_INV),
      .I2 (A6_INV),
      .I3 (WE),
      .O (WE_1)
    );
    FORMAL_AND4 AND_WE_2 (
      .I0 (A4_INV),
      .I1 (A5),
      .I2 (A6_INV),
      .I3 (WE),
      .O (WE_2)
    );
    FORMAL_AND4 AND_WE_3 (
      .I0 (A4),
      .I1 (A5),
      .I2 (A6_INV),
      .I3 (WE),
      .O (WE_3)
    );
    FORMAL_AND4 AND_WE_4 (
      .I0 (A4_INV),
      .I1 (A5_INV),
      .I2 (A6),
      .I3 (WE),
      .O (WE_4)
    );
    FORMAL_AND4 AND_WE_5 (
      .I0 (A4),
      .I1 (A5_INV),
      .I2 (A6),
      .I3 (WE),
      .O (WE_5)
    );
    FORMAL_AND4 AND_WE_6 (
      .I0 (A4_INV),
      .I1 (A5),
      .I2 (A6),
      .I3 (WE),
      .O (WE_6)
    );
    FORMAL_AND4 AND_WE_7 (
      .I0 (A4),
      .I1 (A5),
      .I2 (A6),
      .I3 (WE),
      .O (WE_7)
    );

    FORMAL_RAMD16 RAMD_O_0 (
      .RADR0 (A0),
      .RADR1 (A1),
      .RADR2 (A2),
      .RADR3 (A3),
      .WADR0 (A0),
      .WADR1 (A1),
      .WADR2 (A2),
      .WADR3 (A3),
      .I (D),
      .CLK (WCLK_in),
      .WE (WE_0),
      .O (O_0)
    );
    
    defparam RAMD_O_0.INIT = INIT[15:0];
    
    FORMAL_RAMD16 RAMD_O_1 (
      .RADR0 (A0),
      .RADR1 (A1),
      .RADR2 (A2),
      .RADR3 (A3),
      .WADR0 (A0),
      .WADR1 (A1),
      .WADR2 (A2),
      .WADR3 (A3),
      .I (D),
      .CLK (WCLK_in),
      .WE (WE_1),
      .O (O_1)
    );
    
    defparam RAMD_O_1.INIT = INIT[31:16];
    
    FORMAL_RAMD16 RAMD_O_2 (
      .RADR0 (A0),
      .RADR1 (A1),
      .RADR2 (A2),
      .RADR3 (A3),
      .WADR0 (A0),
      .WADR1 (A1),
      .WADR2 (A2),
      .WADR3 (A3),
      .I (D),
      .CLK (WCLK_in),
      .WE (WE_2),
      .O (O_2)
    );
    
    defparam RAMD_O_2.INIT = INIT[47:32];
    
    FORMAL_RAMD16 RAMD_O_3 (
      .RADR0 (A0),
      .RADR1 (A1),
      .RADR2 (A2),
      .RADR3 (A3),
      .WADR0 (A0),
      .WADR1 (A1),
      .WADR2 (A2),
      .WADR3 (A3),
      .I (D),
      .CLK (WCLK_in),
      .WE (WE_3),
      .O (O_3)
    );
    
    defparam RAMD_O_3.INIT = INIT[63:48];
    
    FORMAL_RAMD16 RAMD_O_4 (
      .RADR0 (A0),
      .RADR1 (A1),
      .RADR2 (A2),
      .RADR3 (A3),
      .WADR0 (A0),
      .WADR1 (A1),
      .WADR2 (A2),
      .WADR3 (A3),
      .I (D),
      .CLK (WCLK_in),
      .WE (WE_4),
      .O (O_4)
    );
    
    defparam RAMD_O_4.INIT = INIT[79:64];
    
    FORMAL_RAMD16 RAMD_O_5 (
      .RADR0 (A0),
      .RADR1 (A1),
      .RADR2 (A2),
      .RADR3 (A3),
      .WADR0 (A0),
      .WADR1 (A1),
      .WADR2 (A2),
      .WADR3 (A3),
      .I (D),
      .CLK (WCLK_in),
      .WE (WE_5),
      .O (O_5)
    );
    
    defparam RAMD_O_5.INIT = INIT[95:80];
    
    FORMAL_RAMD16 RAMD_O_6 (
      .RADR0 (A0),
      .RADR1 (A1),
      .RADR2 (A2),
      .RADR3 (A3),
      .WADR0 (A0),
      .WADR1 (A1),
      .WADR2 (A2),
      .WADR3 (A3),
      .I (D),
      .CLK (WCLK_in),
      .WE (WE_6),
      .O (O_6)
    );
    
    defparam RAMD_O_6.INIT = INIT[111:96];
    
    FORMAL_RAMD16 RAMD_O_7 (
      .RADR0 (A0),
      .RADR1 (A1),
      .RADR2 (A2),
      .RADR3 (A3),
      .WADR0 (A0),
      .WADR1 (A1),
      .WADR2 (A2),
      .WADR3 (A3),
      .I (D),
      .CLK (WCLK_in),
      .WE (WE_7),
      .O (O_7)
    );
    
    defparam RAMD_O_7.INIT = INIT[127:112];

    FORMAL_MUX2 MUX_O_0 (
      .IA (O_0),
      .IB (O_1),
      .SEL (A4),
      .O (O_MUX_0)
    );
    FORMAL_MUX2 MUX_O_1 (
      .IA (O_2),
      .IB (O_3),
      .SEL (A4),
      .O (O_MUX_1)
    );
    FORMAL_MUX2 MUX_O_2 (
      .IA (O_4),
      .IB (O_5),
      .SEL (A4),
      .O (O_MUX_2)
    );
    FORMAL_MUX2 MUX_O_3 (
      .IA (O_6),
      .IB (O_7),
      .SEL (A4),
      .O (O_MUX_3)
    );
    FORMAL_MUX2 MUX_O_4 (
      .IA (O_MUX_0),
      .IB (O_MUX_1),
      .SEL (A5),
      .O (O_MUX_4)
    );
    FORMAL_MUX2 MUX_O_5 (
      .IA (O_MUX_2),
      .IB (O_MUX_3),
      .SEL (A5),
      .O (O_MUX_5)
    );
    FORMAL_MUX2 MUX_O_6 (
      .IA (O_MUX_4),
      .IB (O_MUX_5),
      .SEL (A6),
      .O (O)
    );

endmodule

`endcelldefine
