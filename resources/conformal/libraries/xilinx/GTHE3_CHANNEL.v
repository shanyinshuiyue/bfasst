///////////////////////////////////////////////////////////////////////////////
//  Copyright (c) 1995/2015 Xilinx, Inc.
//  All Right Reserved.
///////////////////////////////////////////////////////////////////////////////
//
//   ____   ___
//  /   /\/   / 
// /___/  \  /     Vendor      : Xilinx 
// \   \   \/      Version     : 2015.4
//  \   \          Description : Xilinx Formal Library Component
//  /   /                        
// /___/   /\      Filename    : GTHE3_CHANNEL.v
// \   \  /  \ 
//  \___\/\___\                    
//                                 
///////////////////////////////////////////////////////////////////////////////
//  Revision:
//
//  End Revision:
///////////////////////////////////////////////////////////////////////////////

`timescale 1 ps / 1 ps 

`celldefine

module GTHE3_CHANNEL #(
  `ifdef XIL_TIMING //Simprim 
  parameter LOC = "UNPLACED",  
  `endif
  parameter [0:0] ACJTAG_DEBUG_MODE = 1'b0,
  parameter [0:0] ACJTAG_MODE = 1'b0,
  parameter [0:0] ACJTAG_RESET = 1'b0,
  parameter [15:0] ADAPT_CFG0 = 16'hF800,
  parameter [15:0] ADAPT_CFG1 = 16'h0000,
  parameter ALIGN_COMMA_DOUBLE = "FALSE",
  parameter [9:0] ALIGN_COMMA_ENABLE = 10'b0001111111,
  parameter integer ALIGN_COMMA_WORD = 1,
  parameter ALIGN_MCOMMA_DET = "TRUE",
  parameter [9:0] ALIGN_MCOMMA_VALUE = 10'b1010000011,
  parameter ALIGN_PCOMMA_DET = "TRUE",
  parameter [9:0] ALIGN_PCOMMA_VALUE = 10'b0101111100,
  parameter [0:0] A_RXOSCALRESET = 1'b0,
  parameter [0:0] A_RXPROGDIVRESET = 1'b0,
  parameter [0:0] A_TXPROGDIVRESET = 1'b0,
  parameter CBCC_DATA_SOURCE_SEL = "DECODED",
  parameter [0:0] CDR_SWAP_MODE_EN = 1'b0,
  parameter CHAN_BOND_KEEP_ALIGN = "FALSE",
  parameter integer CHAN_BOND_MAX_SKEW = 7,
  parameter [9:0] CHAN_BOND_SEQ_1_1 = 10'b0101111100,
  parameter [9:0] CHAN_BOND_SEQ_1_2 = 10'b0000000000,
  parameter [9:0] CHAN_BOND_SEQ_1_3 = 10'b0000000000,
  parameter [9:0] CHAN_BOND_SEQ_1_4 = 10'b0000000000,
  parameter [3:0] CHAN_BOND_SEQ_1_ENABLE = 4'b1111,
  parameter [9:0] CHAN_BOND_SEQ_2_1 = 10'b0100000000,
  parameter [9:0] CHAN_BOND_SEQ_2_2 = 10'b0100000000,
  parameter [9:0] CHAN_BOND_SEQ_2_3 = 10'b0100000000,
  parameter [9:0] CHAN_BOND_SEQ_2_4 = 10'b0100000000,
  parameter [3:0] CHAN_BOND_SEQ_2_ENABLE = 4'b1111,
  parameter CHAN_BOND_SEQ_2_USE = "FALSE",
  parameter integer CHAN_BOND_SEQ_LEN = 2,
  parameter CLK_CORRECT_USE = "TRUE",
  parameter CLK_COR_KEEP_IDLE = "FALSE",
  parameter integer CLK_COR_MAX_LAT = 20,
  parameter integer CLK_COR_MIN_LAT = 18,
  parameter CLK_COR_PRECEDENCE = "TRUE",
  parameter integer CLK_COR_REPEAT_WAIT = 0,
  parameter [9:0] CLK_COR_SEQ_1_1 = 10'b0100011100,
  parameter [9:0] CLK_COR_SEQ_1_2 = 10'b0000000000,
  parameter [9:0] CLK_COR_SEQ_1_3 = 10'b0000000000,
  parameter [9:0] CLK_COR_SEQ_1_4 = 10'b0000000000,
  parameter [3:0] CLK_COR_SEQ_1_ENABLE = 4'b1111,
  parameter [9:0] CLK_COR_SEQ_2_1 = 10'b0100000000,
  parameter [9:0] CLK_COR_SEQ_2_2 = 10'b0100000000,
  parameter [9:0] CLK_COR_SEQ_2_3 = 10'b0100000000,
  parameter [9:0] CLK_COR_SEQ_2_4 = 10'b0100000000,
  parameter [3:0] CLK_COR_SEQ_2_ENABLE = 4'b1111,
  parameter CLK_COR_SEQ_2_USE = "FALSE",
  parameter integer CLK_COR_SEQ_LEN = 2,
  parameter [15:0] CPLL_CFG0 = 16'h20F8,
  parameter [15:0] CPLL_CFG1 = 16'hA494,
  parameter [15:0] CPLL_CFG2 = 16'hF001,
  parameter [5:0] CPLL_CFG3 = 6'h00,
  parameter integer CPLL_FBDIV = 4,
  parameter integer CPLL_FBDIV_45 = 4,
  parameter [15:0] CPLL_INIT_CFG0 = 16'h001E,
  parameter [7:0] CPLL_INIT_CFG1 = 8'h00,
  parameter [15:0] CPLL_LOCK_CFG = 16'h01E8,
  parameter integer CPLL_REFCLK_DIV = 1,
  parameter [1:0] DDI_CTRL = 2'b00,
  parameter integer DDI_REALIGN_WAIT = 15,
  parameter DEC_MCOMMA_DETECT = "TRUE",
  parameter DEC_PCOMMA_DETECT = "TRUE",
  parameter DEC_VALID_COMMA_ONLY = "TRUE",
  parameter [0:0] DFE_D_X_REL_POS = 1'b0,
  parameter [0:0] DFE_VCM_COMP_EN = 1'b0,
  parameter [9:0] DMONITOR_CFG0 = 10'h000,
  parameter [7:0] DMONITOR_CFG1 = 8'h00,
  parameter [0:0] ES_CLK_PHASE_SEL = 1'b0,
  parameter [5:0] ES_CONTROL = 6'b000000,
  parameter ES_ERRDET_EN = "FALSE",
  parameter ES_EYE_SCAN_EN = "FALSE",
  parameter [11:0] ES_HORZ_OFFSET = 12'h000,
  parameter [9:0] ES_PMA_CFG = 10'b0000000000,
  parameter [4:0] ES_PRESCALE = 5'b00000,
  parameter [15:0] ES_QUALIFIER0 = 16'h0000,
  parameter [15:0] ES_QUALIFIER1 = 16'h0000,
  parameter [15:0] ES_QUALIFIER2 = 16'h0000,
  parameter [15:0] ES_QUALIFIER3 = 16'h0000,
  parameter [15:0] ES_QUALIFIER4 = 16'h0000,
  parameter [15:0] ES_QUAL_MASK0 = 16'h0000,
  parameter [15:0] ES_QUAL_MASK1 = 16'h0000,
  parameter [15:0] ES_QUAL_MASK2 = 16'h0000,
  parameter [15:0] ES_QUAL_MASK3 = 16'h0000,
  parameter [15:0] ES_QUAL_MASK4 = 16'h0000,
  parameter [15:0] ES_SDATA_MASK0 = 16'h0000,
  parameter [15:0] ES_SDATA_MASK1 = 16'h0000,
  parameter [15:0] ES_SDATA_MASK2 = 16'h0000,
  parameter [15:0] ES_SDATA_MASK3 = 16'h0000,
  parameter [15:0] ES_SDATA_MASK4 = 16'h0000,
  parameter [10:0] EVODD_PHI_CFG = 11'b00000000000,
  parameter [0:0] EYE_SCAN_SWAP_EN = 1'b0,
  parameter [3:0] FTS_DESKEW_SEQ_ENABLE = 4'b1111,
  parameter [3:0] FTS_LANE_DESKEW_CFG = 4'b1111,
  parameter FTS_LANE_DESKEW_EN = "FALSE",
  parameter [4:0] GEARBOX_MODE = 5'b00000,
  parameter [0:0] GM_BIAS_SELECT = 1'b0,
  parameter [0:0] LOCAL_MASTER = 1'b0,
  parameter [1:0] OOBDIVCTL = 2'b00,
  parameter [0:0] OOB_PWRUP = 1'b0,
  parameter PCI3_AUTO_REALIGN = "FRST_SMPL",
  parameter [0:0] PCI3_PIPE_RX_ELECIDLE = 1'b1,
  parameter [1:0] PCI3_RX_ASYNC_EBUF_BYPASS = 2'b00,
  parameter [0:0] PCI3_RX_ELECIDLE_EI2_ENABLE = 1'b0,
  parameter [5:0] PCI3_RX_ELECIDLE_H2L_COUNT = 6'b000000,
  parameter [2:0] PCI3_RX_ELECIDLE_H2L_DISABLE = 3'b000,
  parameter [5:0] PCI3_RX_ELECIDLE_HI_COUNT = 6'b000000,
  parameter [0:0] PCI3_RX_ELECIDLE_LP4_DISABLE = 1'b0,
  parameter [0:0] PCI3_RX_FIFO_DISABLE = 1'b0,
  parameter [15:0] PCIE_BUFG_DIV_CTRL = 16'h0000,
  parameter [15:0] PCIE_RXPCS_CFG_GEN3 = 16'h0000,
  parameter [15:0] PCIE_RXPMA_CFG = 16'h0000,
  parameter [15:0] PCIE_TXPCS_CFG_GEN3 = 16'h0000,
  parameter [15:0] PCIE_TXPMA_CFG = 16'h0000,
  parameter PCS_PCIE_EN = "FALSE",
  parameter [15:0] PCS_RSVD0 = 16'b0000000000000000,
  parameter [2:0] PCS_RSVD1 = 3'b000,
  parameter [11:0] PD_TRANS_TIME_FROM_P2 = 12'h03C,
  parameter [7:0] PD_TRANS_TIME_NONE_P2 = 8'h19,
  parameter [7:0] PD_TRANS_TIME_TO_P2 = 8'h64,
  parameter [1:0] PLL_SEL_MODE_GEN12 = 2'h0,
  parameter [1:0] PLL_SEL_MODE_GEN3 = 2'h0,
  parameter [15:0] PMA_RSV1 = 16'h0000,
  parameter [2:0] PROCESS_PAR = 3'b010,
  parameter [0:0] RATE_SW_USE_DRP = 1'b0,
  parameter [0:0] RESET_POWERSAVE_DISABLE = 1'b0,
  parameter [4:0] RXBUFRESET_TIME = 5'b00001,
  parameter RXBUF_ADDR_MODE = "FULL",
  parameter [3:0] RXBUF_EIDLE_HI_CNT = 4'b1000,
  parameter [3:0] RXBUF_EIDLE_LO_CNT = 4'b0000,
  parameter RXBUF_EN = "TRUE",
  parameter RXBUF_RESET_ON_CB_CHANGE = "TRUE",
  parameter RXBUF_RESET_ON_COMMAALIGN = "FALSE",
  parameter RXBUF_RESET_ON_EIDLE = "FALSE",
  parameter RXBUF_RESET_ON_RATE_CHANGE = "TRUE",
  parameter integer RXBUF_THRESH_OVFLW = 0,
  parameter RXBUF_THRESH_OVRD = "FALSE",
  parameter integer RXBUF_THRESH_UNDFLW = 4,
  parameter [4:0] RXCDRFREQRESET_TIME = 5'b00001,
  parameter [4:0] RXCDRPHRESET_TIME = 5'b00001,
  parameter [15:0] RXCDR_CFG0 = 16'h0000,
  parameter [15:0] RXCDR_CFG0_GEN3 = 16'h0000,
  parameter [15:0] RXCDR_CFG1 = 16'h0080,
  parameter [15:0] RXCDR_CFG1_GEN3 = 16'h0000,
  parameter [15:0] RXCDR_CFG2 = 16'h07E6,
  parameter [15:0] RXCDR_CFG2_GEN3 = 16'h0000,
  parameter [15:0] RXCDR_CFG3 = 16'h0000,
  parameter [15:0] RXCDR_CFG3_GEN3 = 16'h0000,
  parameter [15:0] RXCDR_CFG4 = 16'h0000,
  parameter [15:0] RXCDR_CFG4_GEN3 = 16'h0000,
  parameter [15:0] RXCDR_CFG5 = 16'h0000,
  parameter [15:0] RXCDR_CFG5_GEN3 = 16'h0000,
  parameter [0:0] RXCDR_FR_RESET_ON_EIDLE = 1'b0,
  parameter [0:0] RXCDR_HOLD_DURING_EIDLE = 1'b0,
  parameter [15:0] RXCDR_LOCK_CFG0 = 16'h5080,
  parameter [15:0] RXCDR_LOCK_CFG1 = 16'h07E0,
  parameter [15:0] RXCDR_LOCK_CFG2 = 16'h7C42,
  parameter [0:0] RXCDR_PH_RESET_ON_EIDLE = 1'b0,
  parameter [15:0] RXCFOK_CFG0 = 16'h4000,
  parameter [15:0] RXCFOK_CFG1 = 16'h0060,
  parameter [15:0] RXCFOK_CFG2 = 16'h000E,
  parameter [6:0] RXDFELPMRESET_TIME = 7'b0001111,
  parameter [15:0] RXDFELPM_KL_CFG0 = 16'h0000,
  parameter [15:0] RXDFELPM_KL_CFG1 = 16'h0032,
  parameter [15:0] RXDFELPM_KL_CFG2 = 16'h0000,
  parameter [15:0] RXDFE_CFG0 = 16'h0A00,
  parameter [15:0] RXDFE_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_GC_CFG0 = 16'h0000,
  parameter [15:0] RXDFE_GC_CFG1 = 16'h7840,
  parameter [15:0] RXDFE_GC_CFG2 = 16'h0000,
  parameter [15:0] RXDFE_H2_CFG0 = 16'h0000,
  parameter [15:0] RXDFE_H2_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_H3_CFG0 = 16'h4000,
  parameter [15:0] RXDFE_H3_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_H4_CFG0 = 16'h2000,
  parameter [15:0] RXDFE_H4_CFG1 = 16'h0003,
  parameter [15:0] RXDFE_H5_CFG0 = 16'h2000,
  parameter [15:0] RXDFE_H5_CFG1 = 16'h0003,
  parameter [15:0] RXDFE_H6_CFG0 = 16'h2000,
  parameter [15:0] RXDFE_H6_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_H7_CFG0 = 16'h2000,
  parameter [15:0] RXDFE_H7_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_H8_CFG0 = 16'h2000,
  parameter [15:0] RXDFE_H8_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_H9_CFG0 = 16'h2000,
  parameter [15:0] RXDFE_H9_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_HA_CFG0 = 16'h2000,
  parameter [15:0] RXDFE_HA_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_HB_CFG0 = 16'h2000,
  parameter [15:0] RXDFE_HB_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_HC_CFG0 = 16'h0000,
  parameter [15:0] RXDFE_HC_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_HD_CFG0 = 16'h0000,
  parameter [15:0] RXDFE_HD_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_HE_CFG0 = 16'h0000,
  parameter [15:0] RXDFE_HE_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_HF_CFG0 = 16'h0000,
  parameter [15:0] RXDFE_HF_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_OS_CFG0 = 16'h8000,
  parameter [15:0] RXDFE_OS_CFG1 = 16'h0000,
  parameter [15:0] RXDFE_UT_CFG0 = 16'h8000,
  parameter [15:0] RXDFE_UT_CFG1 = 16'h0003,
  parameter [15:0] RXDFE_VP_CFG0 = 16'hAA00,
  parameter [15:0] RXDFE_VP_CFG1 = 16'h0033,
  parameter [15:0] RXDLY_CFG = 16'h001F,
  parameter [15:0] RXDLY_LCFG = 16'h0030,
  parameter RXELECIDLE_CFG = "Sigcfg_4",
  parameter integer RXGBOX_FIFO_INIT_RD_ADDR = 4,
  parameter RXGEARBOX_EN = "FALSE",
  parameter [4:0] RXISCANRESET_TIME = 5'b00001,
  parameter [15:0] RXLPM_CFG = 16'h0000,
  parameter [15:0] RXLPM_GC_CFG = 16'h0000,
  parameter [15:0] RXLPM_KH_CFG0 = 16'h0000,
  parameter [15:0] RXLPM_KH_CFG1 = 16'h0002,
  parameter [15:0] RXLPM_OS_CFG0 = 16'h8000,
  parameter [15:0] RXLPM_OS_CFG1 = 16'h0002,
  parameter [8:0] RXOOB_CFG = 9'b000000110,
  parameter RXOOB_CLK_CFG = "PMA",
  parameter [4:0] RXOSCALRESET_TIME = 5'b00011,
  parameter integer RXOUT_DIV = 4,
  parameter [4:0] RXPCSRESET_TIME = 5'b00001,
  parameter [15:0] RXPHBEACON_CFG = 16'h0000,
  parameter [15:0] RXPHDLY_CFG = 16'h2020,
  parameter [15:0] RXPHSAMP_CFG = 16'h2100,
  parameter [15:0] RXPHSLIP_CFG = 16'h6622,
  parameter [4:0] RXPH_MONITOR_SEL = 5'b00000,
  parameter [1:0] RXPI_CFG0 = 2'b00,
  parameter [1:0] RXPI_CFG1 = 2'b00,
  parameter [1:0] RXPI_CFG2 = 2'b00,
  parameter [1:0] RXPI_CFG3 = 2'b00,
  parameter [0:0] RXPI_CFG4 = 1'b0,
  parameter [0:0] RXPI_CFG5 = 1'b1,
  parameter [2:0] RXPI_CFG6 = 3'b000,
  parameter [0:0] RXPI_LPM = 1'b0,
  parameter [0:0] RXPI_VREFSEL = 1'b0,
  parameter RXPMACLK_SEL = "DATA",
  parameter [4:0] RXPMARESET_TIME = 5'b00001,
  parameter [0:0] RXPRBS_ERR_LOOPBACK = 1'b0,
  parameter integer RXPRBS_LINKACQ_CNT = 15,
  parameter integer RXSLIDE_AUTO_WAIT = 7,
  parameter RXSLIDE_MODE = "OFF",
  parameter [0:0] RXSYNC_MULTILANE = 1'b0,
  parameter [0:0] RXSYNC_OVRD = 1'b0,
  parameter [0:0] RXSYNC_SKIP_DA = 1'b0,
  parameter [0:0] RX_AFE_CM_EN = 1'b0,
  parameter [15:0] RX_BIAS_CFG0 = 16'h0AD4,
  parameter [5:0] RX_BUFFER_CFG = 6'b000000,
  parameter [0:0] RX_CAPFF_SARC_ENB = 1'b0,
  parameter integer RX_CLK25_DIV = 8,
  parameter [0:0] RX_CLKMUX_EN = 1'b1,
  parameter [4:0] RX_CLK_SLIP_OVRD = 5'b00000,
  parameter [3:0] RX_CM_BUF_CFG = 4'b1010,
  parameter [0:0] RX_CM_BUF_PD = 1'b0,
  parameter [1:0] RX_CM_SEL = 2'b11,
  parameter [3:0] RX_CM_TRIM = 4'b0100,
  parameter [7:0] RX_CTLE3_LPF = 8'b00000000,
  parameter integer RX_DATA_WIDTH = 20,
  parameter [5:0] RX_DDI_SEL = 6'b000000,
  parameter RX_DEFER_RESET_BUF_EN = "TRUE",
  parameter [3:0] RX_DFELPM_CFG0 = 4'b0110,
  parameter [0:0] RX_DFELPM_CFG1 = 1'b0,
  parameter [0:0] RX_DFELPM_KLKH_AGC_STUP_EN = 1'b1,
  parameter [1:0] RX_DFE_AGC_CFG0 = 2'b00,
  parameter [2:0] RX_DFE_AGC_CFG1 = 3'b100,
  parameter [1:0] RX_DFE_KL_LPM_KH_CFG0 = 2'b01,
  parameter [2:0] RX_DFE_KL_LPM_KH_CFG1 = 3'b010,
  parameter [1:0] RX_DFE_KL_LPM_KL_CFG0 = 2'b01,
  parameter [2:0] RX_DFE_KL_LPM_KL_CFG1 = 3'b010,
  parameter [0:0] RX_DFE_LPM_HOLD_DURING_EIDLE = 1'b0,
  parameter RX_DISPERR_SEQ_MATCH = "TRUE",
  parameter [4:0] RX_DIVRESET_TIME = 5'b00001,
  parameter [0:0] RX_EN_HI_LR = 1'b0,
  parameter [6:0] RX_EYESCAN_VS_CODE = 7'b0000000,
  parameter [0:0] RX_EYESCAN_VS_NEG_DIR = 1'b0,
  parameter [1:0] RX_EYESCAN_VS_RANGE = 2'b00,
  parameter [0:0] RX_EYESCAN_VS_UT_SIGN = 1'b0,
  parameter [0:0] RX_FABINT_USRCLK_FLOP = 1'b0,
  parameter integer RX_INT_DATAWIDTH = 1,
  parameter [0:0] RX_PMA_POWER_SAVE = 1'b0,
  parameter real RX_PROGDIV_CFG = 4.0,
  parameter [2:0] RX_SAMPLE_PERIOD = 3'b101,
  parameter integer RX_SIG_VALID_DLY = 11,
  parameter [0:0] RX_SUM_DFETAPREP_EN = 1'b0,
  parameter [3:0] RX_SUM_IREF_TUNE = 4'b0000,
  parameter [1:0] RX_SUM_RES_CTRL = 2'b00,
  parameter [3:0] RX_SUM_VCMTUNE = 4'b0000,
  parameter [0:0] RX_SUM_VCM_OVWR = 1'b0,
  parameter [2:0] RX_SUM_VREF_TUNE = 3'b000,
  parameter [1:0] RX_TUNE_AFE_OS = 2'b00,
  parameter [0:0] RX_WIDEMODE_CDR = 1'b0,
  parameter RX_XCLK_SEL = "RXDES",
  parameter integer SAS_MAX_COM = 64,
  parameter integer SAS_MIN_COM = 36,
  parameter [3:0] SATA_BURST_SEQ_LEN = 4'b1111,
  parameter [2:0] SATA_BURST_VAL = 3'b100,
  parameter SATA_CPLL_CFG = "VCO_3000MHZ",
  parameter [2:0] SATA_EIDLE_VAL = 3'b100,
  parameter integer SATA_MAX_BURST = 8,
  parameter integer SATA_MAX_INIT = 21,
  parameter integer SATA_MAX_WAKE = 7,
  parameter integer SATA_MIN_BURST = 4,
  parameter integer SATA_MIN_INIT = 12,
  parameter integer SATA_MIN_WAKE = 4,
  parameter SHOW_REALIGN_COMMA = "TRUE",
  parameter SIM_MODE = "FAST",   
  parameter SIM_RECEIVER_DETECT_PASS = "TRUE",
  parameter SIM_RESET_SPEEDUP = "TRUE",
  parameter [0:0] SIM_TX_EIDLE_DRIVE_LEVEL = 1'b0,
  parameter integer SIM_VERSION = 2,
  parameter [1:0] TAPDLY_SET_TX = 2'h0,
  parameter [3:0] TEMPERATUR_PAR = 4'b0010,
  parameter [14:0] TERM_RCAL_CFG = 15'b100001000010000,
  parameter [2:0] TERM_RCAL_OVRD = 3'b000,
  parameter [7:0] TRANS_TIME_RATE = 8'h0E,
  parameter [7:0] TST_RSV0 = 8'h00,
  parameter [7:0] TST_RSV1 = 8'h00,
  parameter TXBUF_EN = "TRUE",
  parameter TXBUF_RESET_ON_RATE_CHANGE = "FALSE",
  parameter [15:0] TXDLY_CFG = 16'h001F,
  parameter [15:0] TXDLY_LCFG = 16'h0030,
  parameter [3:0] TXDRVBIAS_N = 4'b1010,
  parameter [3:0] TXDRVBIAS_P = 4'b1100,
  parameter TXFIFO_ADDR_CFG = "LOW",
  parameter integer TXGBOX_FIFO_INIT_RD_ADDR = 4,
  parameter TXGEARBOX_EN = "FALSE",
  parameter integer TXOUT_DIV = 4,
  parameter [4:0] TXPCSRESET_TIME = 5'b00001,
  parameter [15:0] TXPHDLY_CFG0 = 16'h2020,
  parameter [15:0] TXPHDLY_CFG1 = 16'h0001,
  parameter [15:0] TXPH_CFG = 16'h0980,
  parameter [4:0] TXPH_MONITOR_SEL = 5'b00000,
  parameter [1:0] TXPI_CFG0 = 2'b00,
  parameter [1:0] TXPI_CFG1 = 2'b00,
  parameter [1:0] TXPI_CFG2 = 2'b00,
  parameter [0:0] TXPI_CFG3 = 1'b0,
  parameter [0:0] TXPI_CFG4 = 1'b1,
  parameter [2:0] TXPI_CFG5 = 3'b000,
  parameter [0:0] TXPI_GRAY_SEL = 1'b0,
  parameter [0:0] TXPI_INVSTROBE_SEL = 1'b0,
  parameter [0:0] TXPI_LPM = 1'b0,
  parameter TXPI_PPMCLK_SEL = "TXUSRCLK2",
  parameter [7:0] TXPI_PPM_CFG = 8'b00000000,
  parameter [2:0] TXPI_SYNFREQ_PPM = 3'b000,
  parameter [0:0] TXPI_VREFSEL = 1'b0,
  parameter [4:0] TXPMARESET_TIME = 5'b00001,
  parameter [0:0] TXSYNC_MULTILANE = 1'b0,
  parameter [0:0] TXSYNC_OVRD = 1'b0,
  parameter [0:0] TXSYNC_SKIP_DA = 1'b0,
  parameter integer TX_CLK25_DIV = 8,
  parameter [0:0] TX_CLKMUX_EN = 1'b1,
  parameter integer TX_DATA_WIDTH = 20,
  parameter [5:0] TX_DCD_CFG = 6'b000010,
  parameter [0:0] TX_DCD_EN = 1'b0,
  parameter [5:0] TX_DEEMPH0 = 6'b000000,
  parameter [5:0] TX_DEEMPH1 = 6'b000000,
  parameter [4:0] TX_DIVRESET_TIME = 5'b00001,
  parameter TX_DRIVE_MODE = "DIRECT",
  parameter [2:0] TX_EIDLE_ASSERT_DELAY = 3'b110,
  parameter [2:0] TX_EIDLE_DEASSERT_DELAY = 3'b100,
  parameter [0:0] TX_EML_PHI_TUNE = 1'b0,
  parameter [0:0] TX_FABINT_USRCLK_FLOP = 1'b0,
  parameter [0:0] TX_IDLE_DATA_ZERO = 1'b0,
  parameter integer TX_INT_DATAWIDTH = 1,
  parameter TX_LOOPBACK_DRIVE_HIZ = "FALSE",
  parameter [0:0] TX_MAINCURSOR_SEL = 1'b0,
  parameter [6:0] TX_MARGIN_FULL_0 = 7'b1001110,
  parameter [6:0] TX_MARGIN_FULL_1 = 7'b1001001,
  parameter [6:0] TX_MARGIN_FULL_2 = 7'b1000101,
  parameter [6:0] TX_MARGIN_FULL_3 = 7'b1000010,
  parameter [6:0] TX_MARGIN_FULL_4 = 7'b1000000,
  parameter [6:0] TX_MARGIN_LOW_0 = 7'b1000110,
  parameter [6:0] TX_MARGIN_LOW_1 = 7'b1000100,
  parameter [6:0] TX_MARGIN_LOW_2 = 7'b1000010,
  parameter [6:0] TX_MARGIN_LOW_3 = 7'b1000000,
  parameter [6:0] TX_MARGIN_LOW_4 = 7'b1000000,
  parameter [2:0] TX_MODE_SEL = 3'b000,
  parameter [0:0] TX_PMADATA_OPT = 1'b0,
  parameter [0:0] TX_PMA_POWER_SAVE = 1'b0,
  parameter TX_PROGCLK_SEL = "POSTPI",
  parameter real TX_PROGDIV_CFG = 4.0,
  parameter [0:0] TX_QPI_STATUS_EN = 1'b0,
  parameter [13:0] TX_RXDETECT_CFG = 14'h0032,
  parameter [2:0] TX_RXDETECT_REF = 3'b100,
  parameter [2:0] TX_SAMPLE_PERIOD = 3'b101,
  parameter [0:0] TX_SARC_LPBK_ENB = 1'b0,
  parameter TX_XCLK_SEL = "TXOUT",
  parameter [0:0] USE_PCS_CLK_PHASE_SEL = 1'b0,
  parameter [1:0] WB_MODE = 2'b00
)(
  output [2:0] BUFGTCE,
  output [2:0] BUFGTCEMASK,
  output [8:0] BUFGTDIV,
  output [2:0] BUFGTRESET,
  output [2:0] BUFGTRSTMASK,
  output CPLLFBCLKLOST,
  output CPLLLOCK,
  output CPLLREFCLKLOST,
  output [16:0] DMONITOROUT,
  output [15:0] DRPDO,
  output DRPRDY,
  output EYESCANDATAERROR,
  output GTHTXN,
  output GTHTXP,
  output GTPOWERGOOD,
  output GTREFCLKMONITOR,
  output PCIERATEGEN3,
  output PCIERATEIDLE,
  output [1:0] PCIERATEQPLLPD,
  output [1:0] PCIERATEQPLLRESET,
  output PCIESYNCTXSYNCDONE,
  output PCIEUSERGEN3RDY,
  output PCIEUSERPHYSTATUSRST,
  output PCIEUSERRATESTART,
  output [11:0] PCSRSVDOUT,
  output PHYSTATUS,
  output [7:0] PINRSRVDAS,
  output RESETEXCEPTION,
  output [2:0] RXBUFSTATUS,
  output RXBYTEISALIGNED,
  output RXBYTEREALIGN,
  output RXCDRLOCK,
  output RXCDRPHDONE,
  output RXCHANBONDSEQ,
  output RXCHANISALIGNED,
  output RXCHANREALIGN,
  output [4:0] RXCHBONDO,
  output [1:0] RXCLKCORCNT,
  output RXCOMINITDET,
  output RXCOMMADET,
  output RXCOMSASDET,
  output RXCOMWAKEDET,
  output [15:0] RXCTRL0,
  output [15:0] RXCTRL1,
  output [7:0] RXCTRL2,
  output [7:0] RXCTRL3,
  output [127:0] RXDATA,
  output [7:0] RXDATAEXTENDRSVD,
  output [1:0] RXDATAVALID,
  output RXDLYSRESETDONE,
  output RXELECIDLE,
  output [5:0] RXHEADER,
  output [1:0] RXHEADERVALID,
  output [6:0] RXMONITOROUT,
  output RXOSINTDONE,
  output RXOSINTSTARTED,
  output RXOSINTSTROBEDONE,
  output RXOSINTSTROBESTARTED,
  output RXOUTCLK,
  output RXOUTCLKFABRIC,
  output RXOUTCLKPCS,
  output RXPHALIGNDONE,
  output RXPHALIGNERR,
  output RXPMARESETDONE,
  output RXPRBSERR,
  output RXPRBSLOCKED,
  output RXPRGDIVRESETDONE,
  output RXQPISENN,
  output RXQPISENP,
  output RXRATEDONE,
  output RXRECCLKOUT,
  output RXRESETDONE,
  output RXSLIDERDY,
  output RXSLIPDONE,
  output RXSLIPOUTCLKRDY,
  output RXSLIPPMARDY,
  output [1:0] RXSTARTOFSEQ,
  output [2:0] RXSTATUS,
  output RXSYNCDONE,
  output RXSYNCOUT,
  output RXVALID,
  output [1:0] TXBUFSTATUS,
  output TXCOMFINISH,
  output TXDLYSRESETDONE,
  output TXOUTCLK,
  output TXOUTCLKFABRIC,
  output TXOUTCLKPCS,
  output TXPHALIGNDONE,
  output TXPHINITDONE,
  output TXPMARESETDONE,
  output TXPRGDIVRESETDONE,
  output TXQPISENN,
  output TXQPISENP,
  output TXRATEDONE,
  output TXRESETDONE,
  output TXSYNCDONE,
  output TXSYNCOUT,

  input CFGRESET,
  input CLKRSVD0,
  input CLKRSVD1,
  input CPLLLOCKDETCLK,
  input CPLLLOCKEN,
  input CPLLPD,
  input [2:0] CPLLREFCLKSEL,
  input CPLLRESET,
  input DMONFIFORESET,
  input DMONITORCLK,
  input [8:0] DRPADDR,
  input DRPCLK,
  input [15:0] DRPDI,
  input DRPEN,
  input DRPWE,
  input EVODDPHICALDONE,
  input EVODDPHICALSTART,
  input EVODDPHIDRDEN,
  input EVODDPHIDWREN,
  input EVODDPHIXRDEN,
  input EVODDPHIXWREN,
  input EYESCANMODE,
  input EYESCANRESET,
  input EYESCANTRIGGER,
  input GTGREFCLK,
  input GTHRXN,
  input GTHRXP,
  input GTNORTHREFCLK0,
  input GTNORTHREFCLK1,
  input GTREFCLK0,
  input GTREFCLK1,
  input GTRESETSEL,
  input [15:0] GTRSVD,
  input GTRXRESET,
  input GTSOUTHREFCLK0,
  input GTSOUTHREFCLK1,
  input GTTXRESET,
  input [2:0] LOOPBACK,
  input LPBKRXTXSEREN,
  input LPBKTXRXSEREN,
  input PCIEEQRXEQADAPTDONE,
  input PCIERSTIDLE,
  input PCIERSTTXSYNCSTART,
  input PCIEUSERRATEDONE,
  input [15:0] PCSRSVDIN,
  input [4:0] PCSRSVDIN2,
  input [4:0] PMARSVDIN,
  input QPLL0CLK,
  input QPLL0REFCLK,
  input QPLL1CLK,
  input QPLL1REFCLK,
  input RESETOVRD,
  input RSTCLKENTX,
  input RX8B10BEN,
  input RXBUFRESET,
  input RXCDRFREQRESET,
  input RXCDRHOLD,
  input RXCDROVRDEN,
  input RXCDRRESET,
  input RXCDRRESETRSV,
  input RXCHBONDEN,
  input [4:0] RXCHBONDI,
  input [2:0] RXCHBONDLEVEL,
  input RXCHBONDMASTER,
  input RXCHBONDSLAVE,
  input RXCOMMADETEN,
  input [1:0] RXDFEAGCCTRL,
  input RXDFEAGCHOLD,
  input RXDFEAGCOVRDEN,
  input RXDFELFHOLD,
  input RXDFELFOVRDEN,
  input RXDFELPMRESET,
  input RXDFETAP10HOLD,
  input RXDFETAP10OVRDEN,
  input RXDFETAP11HOLD,
  input RXDFETAP11OVRDEN,
  input RXDFETAP12HOLD,
  input RXDFETAP12OVRDEN,
  input RXDFETAP13HOLD,
  input RXDFETAP13OVRDEN,
  input RXDFETAP14HOLD,
  input RXDFETAP14OVRDEN,
  input RXDFETAP15HOLD,
  input RXDFETAP15OVRDEN,
  input RXDFETAP2HOLD,
  input RXDFETAP2OVRDEN,
  input RXDFETAP3HOLD,
  input RXDFETAP3OVRDEN,
  input RXDFETAP4HOLD,
  input RXDFETAP4OVRDEN,
  input RXDFETAP5HOLD,
  input RXDFETAP5OVRDEN,
  input RXDFETAP6HOLD,
  input RXDFETAP6OVRDEN,
  input RXDFETAP7HOLD,
  input RXDFETAP7OVRDEN,
  input RXDFETAP8HOLD,
  input RXDFETAP8OVRDEN,
  input RXDFETAP9HOLD,
  input RXDFETAP9OVRDEN,
  input RXDFEUTHOLD,
  input RXDFEUTOVRDEN,
  input RXDFEVPHOLD,
  input RXDFEVPOVRDEN,
  input RXDFEVSEN,
  input RXDFEXYDEN,
  input RXDLYBYPASS,
  input RXDLYEN,
  input RXDLYOVRDEN,
  input RXDLYSRESET,
  input [1:0] RXELECIDLEMODE,
  input RXGEARBOXSLIP,
  input RXLATCLK,
  input RXLPMEN,
  input RXLPMGCHOLD,
  input RXLPMGCOVRDEN,
  input RXLPMHFHOLD,
  input RXLPMHFOVRDEN,
  input RXLPMLFHOLD,
  input RXLPMLFKLOVRDEN,
  input RXLPMOSHOLD,
  input RXLPMOSOVRDEN,
  input RXMCOMMAALIGNEN,
  input [1:0] RXMONITORSEL,
  input RXOOBRESET,
  input RXOSCALRESET,
  input RXOSHOLD,
  input [3:0] RXOSINTCFG,
  input RXOSINTEN,
  input RXOSINTHOLD,
  input RXOSINTOVRDEN,
  input RXOSINTSTROBE,
  input RXOSINTTESTOVRDEN,
  input RXOSOVRDEN,
  input [2:0] RXOUTCLKSEL,
  input RXPCOMMAALIGNEN,
  input RXPCSRESET,
  input [1:0] RXPD,
  input RXPHALIGN,
  input RXPHALIGNEN,
  input RXPHDLYPD,
  input RXPHDLYRESET,
  input RXPHOVRDEN,
  input [1:0] RXPLLCLKSEL,
  input RXPMARESET,
  input RXPOLARITY,
  input RXPRBSCNTRESET,
  input [3:0] RXPRBSSEL,
  input RXPROGDIVRESET,
  input RXQPIEN,
  input [2:0] RXRATE,
  input RXRATEMODE,
  input RXSLIDE,
  input RXSLIPOUTCLK,
  input RXSLIPPMA,
  input RXSYNCALLIN,
  input RXSYNCIN,
  input RXSYNCMODE,
  input [1:0] RXSYSCLKSEL,
  input RXUSERRDY,
  input RXUSRCLK,
  input RXUSRCLK2,
  input SIGVALIDCLK,
  input [19:0] TSTIN,
  input [7:0] TX8B10BBYPASS,
  input TX8B10BEN,
  input [2:0] TXBUFDIFFCTRL,
  input TXCOMINIT,
  input TXCOMSAS,
  input TXCOMWAKE,
  input [15:0] TXCTRL0,
  input [15:0] TXCTRL1,
  input [7:0] TXCTRL2,
  input [127:0] TXDATA,
  input [7:0] TXDATAEXTENDRSVD,
  input TXDEEMPH,
  input TXDETECTRX,
  input [3:0] TXDIFFCTRL,
  input TXDIFFPD,
  input TXDLYBYPASS,
  input TXDLYEN,
  input TXDLYHOLD,
  input TXDLYOVRDEN,
  input TXDLYSRESET,
  input TXDLYUPDOWN,
  input TXELECIDLE,
  input [5:0] TXHEADER,
  input TXINHIBIT,
  input TXLATCLK,
  input [6:0] TXMAINCURSOR,
  input [2:0] TXMARGIN,
  input [2:0] TXOUTCLKSEL,
  input TXPCSRESET,
  input [1:0] TXPD,
  input TXPDELECIDLEMODE,
  input TXPHALIGN,
  input TXPHALIGNEN,
  input TXPHDLYPD,
  input TXPHDLYRESET,
  input TXPHDLYTSTCLK,
  input TXPHINIT,
  input TXPHOVRDEN,
  input TXPIPPMEN,
  input TXPIPPMOVRDEN,
  input TXPIPPMPD,
  input TXPIPPMSEL,
  input [4:0] TXPIPPMSTEPSIZE,
  input TXPISOPD,
  input [1:0] TXPLLCLKSEL,
  input TXPMARESET,
  input TXPOLARITY,
  input [4:0] TXPOSTCURSOR,
  input TXPOSTCURSORINV,
  input TXPRBSFORCEERR,
  input [3:0] TXPRBSSEL,
  input [4:0] TXPRECURSOR,
  input TXPRECURSORINV,
  input TXPROGDIVRESET,
  input TXQPIBIASEN,
  input TXQPISTRONGPDOWN,
  input TXQPIWEAKPUP,
  input [2:0] TXRATE,
  input TXRATEMODE,
  input [6:0] TXSEQUENCE,
  input TXSWING,
  input TXSYNCALLIN,
  input TXSYNCIN,
  input TXSYNCMODE,
  input [1:0] TXSYSCLKSEL,
  input TXUSERRDY,
  input TXUSRCLK,
  input TXUSRCLK2
);

endmodule

`endcelldefine
