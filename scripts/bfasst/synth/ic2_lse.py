import os
import shutil
import subprocess

import bfasst
from bfasst.synth.base import SynthesisTool
from bfasst.status import Status, SynthStatus

PROJECT_TEMPLATE_FILE = 'template_lse.prj'
IC2_LSE_PROJ_FILE = 'lse_project.prj'

class IC2_LSE_SynthesisTool(SynthesisTool):
    def create_netlist(self, design):
        
        # Create project directory
        proj_dir = self.make_project_folder(self.cwd)

        # Save edif netlist path to design object
        design.netlist_path = os.path.join(self.cwd, design.top + ".edf")

        # Create Icecube 2 LSE synthesis project file
        edif_path_temp = os.path.join(proj_dir, design.top + ".edf")
        prj_path = self.create_ic2_lse_project_file(design, proj_dir, edif_path_temp)

        # Run Icecube 2 LSE synthesis
        status = self.run_sythesis(prj_path, proj_dir)
        
        # Copy edif netlist out of project directory3
        if not os.path.isfile(edif_path_temp):
            return Status(SynthStatus.ERROR)
        shutil.copyfile(edif_path_temp, design.netlist_path)

        return status


    def run_sythesis(self, prj_path, proj_dir):
        synth_log_file = os.path.join(proj_dir, bfasst.config.SYNTH_LOG_NAME)

        cmd = [os.path.join(bfasst.config.IC2_INSTALL_DIR, "LSE", "bin", "lin64", "synthesis"), "-f", prj_path]
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = os.path.join(bfasst.config.IC2_INSTALL_DIR, "LSE", "bin", "lin64")
        env["FOUNDRY"] = os.path.join(bfasst.config.IC2_INSTALL_DIR, "LSE")
        env["SBT_DIR"] = os.path.join(bfasst.config.IC2_INSTALL_DIR, "sbt_backend")
        with open(synth_log_file, 'w') as fp:
            p = subprocess.run(cmd, stdout = fp, stderr = subprocess.STDOUT, cwd = proj_dir, env = env)
            if p.returncode != 0:
                return Status(SynthStatus.ERROR)
            
            return Status(SynthStatus.SUCCESS)
        
    def create_ic2_lse_project_file(self, design, proj_dir, edif_path):
        assert type(design) is bfasst.design.Design

        template_file = os.path.join(bfasst.I2C_RESOURCES, PROJECT_TEMPLATE_FILE)
        project_file = os.path.join(proj_dir, IC2_LSE_PROJ_FILE)
        shutil.copyfile(template_file, project_file)
        
        with open(project_file, 'a') as fp:
            fp.write("-p " + design.full_dir + "\n")

            if design.topIsVerilog():
                fp.write("-lib work -ver " + design.top_file + "\n")
            elif design.topIsVHDL():
                fp.write("-lib work -vhd " + design.top_file + "\n")

    # 	@$(foreach var, $(VERILOG_SUPPORT_FILES), echo "-ver $(var)" >> $@;)
    # 	@# @$(foreach var, $(VHDL_SUPPORT_FILES), echo "-lib $(firstword $(subst /, ,$(var))) -vhd $(var)" >> $@;)	
        
    # 	@$(foreach var, $(VHDL_LIB_FILES), echo "-lib $(firstword $(subst /, ,$(var))) -vhd $(VHDL_LIBS_DIR)/$(var)" >> $@;)	
            fp.write("-top " + design.top + "\n")
            fp.write("-output_edif " + edif_path + "\n")

    # 	@echo "-top $(NAME)" >> $@
    # 	@echo "-output_edif ../../$(IC2_EDIF_FILE)" >> $@
        return project_file

    def make_project_folder(self, build_dir):
        ic2_proj_dir = os.path.join(build_dir, bfasst.config.I2C_SYNTH_FOLDER)

        if not os.path.isdir(ic2_proj_dir):
            os.mkdir(ic2_proj_dir)
            return ic2_proj_dir