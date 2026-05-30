# ----------------------------------------------
# Script Recorded by ANSYS Electronics Desktop Version 2018.0.0
# 8:11:03  May 14, 2026
# ----------------------------------------------
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.SetActiveProject("SRM_12_8_Optim")
oDesign = oProject.SetActiveDesign("oMaxwell2DDesig_Conditional1")
oModule = oDesign.GetModule("ReportSetup")
oModule.CreateReport("Winding Plot 5", "Transient", "3D Rectangular Plot", "Setup1 : Transient", [], 
	[
		"Time:="		, ["All"],
		"I_aa:="		, ["All"],
		"RotorYoke:="		, ["Nominal"],
		"RotorPoleArcByPolePitch:=", ["Nominal"],
		"StatorOuterRadius:="	, ["Nominal"],
		"gap:="			, ["Nominal"],
		"StatorYoke:="		, ["Nominal"],
		"StatorPoleArcByPolePitch:=", ["Nominal"],
		"ThetaR:="		, ["0deg"],
		"I_b:="			, ["Nominal"],
		"I_c:="			, ["Nominal"],
		"param:="		, ["0"],
		"ThI:="			, ["Nominal"],
		"Thf:="			, ["Nominal"],
		"RotorOuterRadius:="	, ["49.6mm"],
		"Nc:="			, ["10"],
		"Spdr:="		, ["Nominal"]
	], 
	[
		"X Component:="		, "Moving1.Position",
		"Y Component:="		, "I_aa",
		"Z Component:="		, ["FluxLinkage(A)"]
	], [])
oModule.CreateReport("Torque Plot 3", "Transient", "3D Rectangular Plot", "Setup1 : Transient", [], 
	[
		"Time:="		, ["All"],
		"I_aa:="		, ["All"],
		"RotorYoke:="		, ["Nominal"],
		"RotorPoleArcByPolePitch:=", ["Nominal"],
		"StatorOuterRadius:="	, ["Nominal"],
		"gap:="			, ["Nominal"],
		"StatorYoke:="		, ["Nominal"],
		"StatorPoleArcByPolePitch:=", ["Nominal"],
		"ThetaR:="		, ["0deg"],
		"I_b:="			, ["Nominal"],
		"I_c:="			, ["Nominal"],
		"param:="		, ["0"],
		"ThI:="			, ["Nominal"],
		"Thf:="			, ["Nominal"],
		"RotorOuterRadius:="	, ["49.6mm"],
		"Nc:="			, ["10"],
		"Spdr:="		, ["Nominal"]
	], 
	[
		"X Component:="		, "Moving1.Position",
		"Y Component:="		, "I_aa",
		"Z Component:="		, ["Moving1.Torque"]
	], [])
oModule.CreateReport("Torque Plot 4", "Transient", "3D Rectangular Plot", "Setup1 : Transient", [], 
	[
		"Time:="		, ["All"],
		"I_aa:="		, ["All"],
		"RotorYoke:="		, ["Nominal"],
		"RotorPoleArcByPolePitch:=", ["Nominal"],
		"StatorOuterRadius:="	, ["Nominal"],
		"gap:="			, ["Nominal"],
		"StatorYoke:="		, ["Nominal"],
		"StatorPoleArcByPolePitch:=", ["Nominal"],
		"ThetaR:="		, ["0deg"],
		"I_b:="			, ["Nominal"],
		"I_c:="			, ["Nominal"],
		"param:="		, ["0"],
		"ThI:="			, ["Nominal"],
		"Thf:="			, ["Nominal"],
		"RotorOuterRadius:="	, ["49.6mm"],
		"Nc:="			, ["10"],
		"Spdr:="		, ["Nominal"]
	], 
	[
		"X Component:="		, "Moving1.Position",
		"Y Component:="		, "I_aa",
		"Z Component:="		, ["Torque1.Torque"]
	], [])
