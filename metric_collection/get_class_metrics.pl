use strict;
use Understand;
use File::Path;

# "accumulo", "activemq", "any23", "camel", "flink", "gora", "ivy", "kafka", "kylin", "lens", "mnemonic", "nutch", "storm", "struts", "tika", "zeppelin", "zookeeper"
my @projects = ("mnemonic");

my $root_path = "F:/BugDetection/Project";

foreach my $project (@projects)
{
	my $path = "$root_path/Releases/$project/";
	opendir DIR, $path or die "Can not open \"$path\"";
	unless (-e "$root_path/Class_Metrics/$project/")
	{
		mkpath "$root_path/Class_Metrics/$project/";
	}

	my @filelist = readdir DIR;
	foreach my $file_name (@filelist)
	{
		next if ($file_name eq "." or $file_name eq "..");
		next unless ($file_name =~ /.udb/);
		$file_name =~ /(.*?).udb/;
		$file_name = $1;
		
		my $udb_dir = "$root_path/Releases/$project/$file_name.udb";
		my $out_dir = "$root_path/Class_Metrics/$project/$file_name.csv";
		my $sub_str = "$root_path/Releases/$project/$file_name/";

		print $file_name, "\n";

		get_metrics($udb_dir, $out_dir, $sub_str);
	}
}


sub get_metrics
{
	my($udb_dir, $out_dir, $sub_str) = @_;
	(my $db, my $status) = Understand::open($udb_dir);
	if(!$db)
	{
		die "Error opening .udb database: $status\n" if $status;
	}

	# The entities list
	my @ents = $db->ents("class,interface ~unknown ~unresolved");

	my @lines = ();
	
	push(@lines, "id,kind_longname,kind,longname,name,simplename,file,start_line,end_line,SLOC,CLOC,CCR,CC_sum,CC_avg,CC_max,EC_sum,EC_avg,EC_max,Nesting,NCB,CBO,NOC,NCM,NCV,NIM,NIV,WMC,RFC,NDM,NPRM,NPTM,NPM,DIT,LCOM\n");

	# 逐次访问每个实体列表
	foreach my $ent (@ents)
	{
		my $define_ref = $ent->ref("definein");
		next unless(defined $define_ref);

		my $end_ref = $ent->ref("endby");
		next unless(defined $end_ref);

		my $id = $ent->id();

		my $kind_longname = $ent->kind()->longname();
		my $kind = $ent->kind()->name();

		my $longname = $ent->longname();
		my $name = $ent->name();
		my $simplename = $ent->simplename();

		my $file = $define_ref->file->longname();
		next if ($file =~ m/Program Files\\Java\\jdk/);
		$file =~ s/\\/\//g;

		$file = substr($file, length($sub_str), length($file)-length($sub_str));

		my $start_line = $define_ref->line();
		my $end_line = $end_ref->line();

		## Size 3 ##
		my $SLOC = $ent->metric("CountLineCode");
		my $CLOC = $ent->metric("CountLineComment");
		my $CCR = $ent->metric("RatioCommentToCode");

		## Complexity 7 ##
		my $CC_sum = $ent->metric("SumCyclomatic");
		my $CC_avg = $ent->metric("AvgCyclomatic");
		my $CC_max = $ent->metric("MaxCyclomatic");

		my $EC_sum = $ent->metric("SumEssential");
		my $EC_avg = $ent->metric("AvgEssential");
		my $EC_max = $ent->metric("MaxEssential");

		my $Nesting = $ent->metric("MaxNesting");

		## OO 5 + 10 ##
		my $NCB = $ent->metric("CountClassBase");
		my $CBO = $ent->metric("CountClassCoupled");
		my $NOC = $ent->metric("CountClassDerived");
		my $DIT = $ent->metric("MaxInheritanceTree");
		my $LCOM = $ent->metric("PercentLackOfCohesion");


		my $RFC = $ent->metric("CountDeclMethodAll"); # all available method including inherited ones
		my $WMC = $ent->metric("CountDeclMethod");

		my $NCM = $ent->metric("CountDeclClassMethod");       # static method
		my $NCV = $ent->metric("CountDeclClassVariable");     # static variable
		my $NIM = $ent->metric("CountDeclInstanceMethod");    # instance method
		my $NIV = $ent->metric("CountDeclInstanceVariable");  # instance variable

		my $NDM = $ent->metric("CountDeclMethodDefault");    # default
		my $NPRM = $ent->metric("CountDeclMethodPrivate");   # private
		my $NPTM = $ent->metric("CountDeclMethodProtected"); # protected
		my $NPM = $ent->metric("CountDeclMethodPublic");     # public

		push(@lines, "$id,$kind_longname,$kind,$longname,$name,$simplename,$file,$start_line,$end_line,$SLOC,$CLOC,$CCR,$CC_sum,$CC_avg,$CC_max,$EC_sum,$EC_avg,$EC_max,$Nesting,$NCB,$CBO,$NOC,$NCM,$NCV,$NIM,$NIV,$WMC,$RFC,$NDM,$NPRM,$NPTM,$NPM,$DIT,$LCOM\n");

	}
	
	$db->close();

	open FILE, ">$out_dir";
	print FILE @lines;
	close(FILE);
}
