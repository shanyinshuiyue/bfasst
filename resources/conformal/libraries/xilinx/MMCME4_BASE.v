///////////////////////////////////////////////////////////////////////////////
//  Copyright (c) 1995/2016 Xilinx, Inc.
//  All Right Reserved.
///////////////////////////////////////////////////////////////////////////////
//   ____  ____
//  /   /\/   /
// /___/  \  /     Vendor      : Xilinx
// \   \   \/      Version     : 2016.1
//  \   \          Description : Xilinx Formal Library Component
//  /   /                        Base Mixed Mode Clock Manager (MMCM)
// /___/   /\      Filename    : MMCME4_BASE.v
// \   \  /  \
//  \___\/\___\
//
///////////////////////////////////////////////////////////////////////////////
//  Revision:
//  10/31/2014 828995 - Added inverter functionality for IS_*_INVERTED parameter
//  End Revision:
///////////////////////////////////////////////////////////////////////////////

`timescale 1 ps / 1 ps

`celldefine

module MMCME4_BASE #(
`ifdef XIL_TIMING
  parameter LOC = "UNPLACED",
`endif
  parameter BANDWIDTH = "OPTIMIZED",
  parameter real CLKFBOUT_MULT_F = 5.000,
  parameter real CLKFBOUT_PHASE = 0.000,
  parameter real CLKIN1_PERIOD = 0.000,
  parameter real CLKOUT0_DIVIDE_F = 1.000,
  parameter real CLKOUT0_DUTY_CYCLE = 0.500,
  parameter real CLKOUT0_PHASE = 0.000,
  parameter integer CLKOUT1_DIVIDE = 1,
  parameter real CLKOUT1_DUTY_CYCLE = 0.500,
  parameter real CLKOUT1_PHASE = 0.000,
  parameter integer CLKOUT2_DIVIDE = 1,
  parameter real CLKOUT2_DUTY_CYCLE = 0.500,
  parameter real CLKOUT2_PHASE = 0.000,
  parameter integer CLKOUT3_DIVIDE = 1,
  parameter real CLKOUT3_DUTY_CYCLE = 0.500,
  parameter real CLKOUT3_PHASE = 0.000,
  parameter CLKOUT4_CASCADE = "FALSE",
  parameter integer CLKOUT4_DIVIDE = 1,
  parameter real CLKOUT4_DUTY_CYCLE = 0.500,
  parameter real CLKOUT4_PHASE = 0.000,
  parameter integer CLKOUT5_DIVIDE = 1,
  parameter real CLKOUT5_DUTY_CYCLE = 0.500,
  parameter real CLKOUT5_PHASE = 0.000,
  parameter integer CLKOUT6_DIVIDE = 1,
  parameter real CLKOUT6_DUTY_CYCLE = 0.500,
  parameter real CLKOUT6_PHASE = 0.000,
  parameter integer DIVCLK_DIVIDE = 1,
  parameter [0:0] IS_CLKFBIN_INVERTED = 1'b0,
  parameter [0:0] IS_CLKIN1_INVERTED = 1'b0,
  parameter [0:0] IS_PWRDWN_INVERTED = 1'b0,
  parameter [0:0] IS_RST_INVERTED = 1'b0,
  parameter real REF_JITTER1 = 0.010,
  parameter STARTUP_WAIT = "FALSE"
)(
  output CLKFBOUT,
  output CLKFBOUTB,
  output CLKOUT0,
  output CLKOUT0B,
  output CLKOUT1,
  output CLKOUT1B,
  output CLKOUT2,
  output CLKOUT2B,
  output CLKOUT3,
  output CLKOUT3B,
  output CLKOUT4,
  output CLKOUT5,
  output CLKOUT6,
  output LOCKED,

  input CLKFBIN,
  input CLKIN1,
  input PWRDWN,
  input RST
);

  wire CLKFBIN_in;
  wire CLKIN1_in;
  wire PWRDWN_in;
  wire RST_in;
  wire RST_PWRDWN_in;

  assign CLKFBIN_in = CLKFBIN ^ IS_CLKFBIN_INVERTED;
  assign CLKIN1_in = CLKIN1 ^ IS_CLKIN1_INVERTED;
  assign PWRDWN_in = PWRDWN ^ IS_PWRDWN_INVERTED;
  assign RST_in = RST ^ IS_RST_INVERTED;
  assign RST_PWRDWN_in = RST_in | PWRDWN_in;

  MMCME4_BASE_bb inst_bb (
               .CLKFBOUT(CLKFBOUT),
               .CLKFBOUTB(CLKFBOUTB),
               .CLKOUT0(CLKOUT0),
               .CLKOUT0B(CLKOUT0B),
               .CLKOUT1(CLKOUT1),
               .CLKOUT1B(CLKOUT1B),
               .CLKOUT2(CLKOUT2),
               .CLKOUT2B(CLKOUT2B),
               .CLKOUT3(CLKOUT3),
               .CLKOUT3B(CLKOUT3B),
               .CLKOUT4(CLKOUT4),
               .CLKOUT5(CLKOUT5),
               .CLKOUT6(CLKOUT6),
               .LOCKED(LOCKED),
               .CLKFBIN(CLKFBIN_in),
               .CLKIN1(CLKIN1_in),
               .PWRDWN(RST_PWRDWN_in),
               .RST(RST_PWRDWN_in)
               );

endmodule

module MMCME4_BASE_bb (
  output CLKFBOUT,
  output CLKFBOUTB,
  output CLKOUT0,
  output CLKOUT0B,
  output CLKOUT1,
  output CLKOUT1B,
  output CLKOUT2,
  output CLKOUT2B,
  output CLKOUT3,
  output CLKOUT3B,
  output CLKOUT4,
  output CLKOUT5,
  output CLKOUT6,
  output LOCKED,

  input CLKFBIN,
  input CLKIN1,
  input PWRDWN,
  input RST
);

endmodule

`endcelldefine
