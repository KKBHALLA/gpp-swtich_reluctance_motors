# ----------------------------------------------
# Script Recorded by ANSYS Electronics Desktop Version 2018.0.0
# 16:34:23  May 12, 2026
# ----------------------------------------------
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.SetActiveProject("SRM_12_8_Optim")
oDesign = oProject.SetActiveDesign("oMaxwell2DDesig_Conditional1")
oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:RotorOuterRadius",
					"Value:="		, "49.5mm"
				]
			]
		]
	])
oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:RotorOuterRadius",
					"Value:="		, "49.6mm"
				]
			]
		]
	])
oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:RotorYoke",
					"Value:="		, "14mm"
				]
			]
		]
	])
oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:RotorYoke",
					"Value:="		, "15mm"
				]
			]
		]
	])
oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:StatorOuterRadius",
					"Value:="		, "81mm"
				]
			]
		]
	])
oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:StatorOuterRadius",
					"Value:="		, "80mm"
				]
			]
		]
	])
oModule = oDesign.GetModule("ReportSetup")
oModule.DeleteAllReports()
oProject.Save()
oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:Nc",
					"Value:="		, "10"
				]
			]
		]
	])
oDesign.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:LocalVariableTab",
			[
				"NAME:PropServers", 
				"LocalVariables"
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:I_aa",
					"Value:="		, "92A"
				]
			]
		]
	])
oProject.Save()
oDesign.Analyze("Setup1")
oModule.CreateReport("Winding Plot 1", "Transient", "Rectangular Plot", "Setup1 : Transient", 
	[
		"Domain:="		, "Sweep"
	], 
	[
		"Time:="		, ["All"],
		"RotorOuterRadius:="	, ["All"],
		"RotorYoke:="		, ["Nominal"],
		"RotorPoleArcByPolePitch:=", ["Nominal"],
		"StatorOuterRadius:="	, ["Nominal"],
		"gap:="			, ["Nominal"],
		"StatorYoke:="		, ["Nominal"],
		"StatorPoleArcByPolePitch:=", ["Nominal"],
		"ThetaR:="		, ["All"],
		"I_b:="			, ["Nominal"],
		"I_c:="			, ["Nominal"],
		"param:="		, ["All"],
		"ThI:="			, ["Nominal"],
		"Thf:="			, ["Nominal"],
		"I_aa:="		, ["Nominal"],
		"Nc:="			, ["All"],
		"Spdr:="		, ["Nominal"]
	], 
	[
		"X Component:="		, "Moving1.Position",
		"Y Component:="		, ["FluxLinkage(A)"]
	], [])
oModule = oDesign.GetModule("ModelSetup")
oModule.EditMotionSetup("MotionSetup1", 
	[
		"NAME:Data",
		"Move Type:="		, "Rotate",
		"Coordinate System:="	, "Global",
		"Axis:="		, "Z",
		"Is Positive:="		, True,
		"InitPos:="		, "-7.5deg",
		"HasRotateLimit:="	, False,
		"NonCylindrical:="	, False,
		"Consider Mechanical Transient:=", False,
		"Angular Velocity:="	, "Spdr"
	])
oDesign.DeleteFullVariation("All", False)
oModule = oDesign.GetModule("Optimetrics")
oModule.EditSetup("Iaa", 
	[
		"NAME:Iaa",
		"IsEnabled:="		, True,
		[
			"NAME:ProdOptiSetupDataV2",
			"SaveFields:="		, False,
			"CopyMesh:="		, False,
			"SolveWithCopiedMeshOnly:=", False
		],
		[
			"NAME:StartingPoint",
			"I_aa:="		, "92A"
		],
		"Sim. Setups:="		, ["Setup1"],
		[
			"NAME:Sweeps",
			[
				"NAME:SweepDefinition",
				"Variable:="		, "I_aa",
				"Data:="		, "LINC 0A 115A 10",
				"OffsetF1:="		, False,
				"Synchronize:="		, 0
			]
		],
		[
			"NAME:Sweep Operations"
		],
		[
			"NAME:Goals"
		]
	])
oProject.Save()
oModule.SolveSetup("Iaa")
oModule = oDesign.GetModule("ReportSetup")
oModule.CreateReport("Winding Plot 2", "Transient", "Rectangular Plot", "Setup1 : Transient", 
	[
		"Domain:="		, "Sweep"
	], 
	[
		"Time:="		, ["All"],
		"RotorOuterRadius:="	, ["All"],
		"RotorYoke:="		, ["Nominal"],
		"RotorPoleArcByPolePitch:=", ["Nominal"],
		"StatorOuterRadius:="	, ["Nominal"],
		"gap:="			, ["Nominal"],
		"StatorYoke:="		, ["Nominal"],
		"StatorPoleArcByPolePitch:=", ["Nominal"],
		"ThetaR:="		, ["All"],
		"I_b:="			, ["Nominal"],
		"I_c:="			, ["Nominal"],
		"param:="		, ["All"],
		"ThI:="			, ["Nominal"],
		"Thf:="			, ["Nominal"],
		"I_aa:="		, ["All"],
		"Nc:="			, ["All"],
		"Spdr:="		, ["Nominal"]
	], 
	[
		"X Component:="		, "Moving1.Position",
		"Y Component:="		, ["FluxLinkage(A)"]
	], [])
oModule.ExportToFile("Winding Plot 2", "D:/Ansys/ConsultancyWork/GPP/Design/Winding Plot 2.csv")
oModule.CreateReport("Winding Plot 3", "Transient", "3D Rectangular Plot", "Setup1 : Transient", [], 
	[
		"Time:="		, ["All"],
		"RotorOuterRadius:="	, ["All"],
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
		"I_aa:="		, ["0A"],
		"Nc:="			, ["10"],
		"Spdr:="		, ["Nominal"]
	], 
	[
		"X Component:="		, "Moving1.Position",
		"Y Component:="		, "I_aa",
		"Z Component:="		, ["FluxLinkage(A)"]
	], [])
oModule.CreateReport("Winding Plot 4", "Transient", "3D Rectangular Plot", "Setup1 : Transient", [], 
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
oModule.ExportToFile("Winding Plot 4", "D:/Ansys/ConsultancyWork/GPP/Design/Winding Plot 4.csv")
