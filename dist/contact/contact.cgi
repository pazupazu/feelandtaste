#!/usr/bin/perl
##!C:/Perl5.6/bin/Perl


require './regist.cfg';
require './jcode.pl';
require './cgi-lib.pl';
require './mimew.pl';
use Time::Local;

# ======================================================
# �����ݒ�
# ======================================================

$sendmail = $CFG_SENDMAIL;
$nkf = $CFG_NKF;
$mailto = $CFG_MAILTO;							# ���[���̈���(�N���C�A���g)
$title    = '���₢���킹������܂���'; # ���[���̃^�C�g��(�N���C�A���g��)
$titlerep    = '�yFEEL AND TASTE�z���₢��������t���܂���'; # ���[���̃^�C�g��(�����҈�)
$kakuninhtml = "./contact_check.html";				# �m�F��ʗpHTML 
$thankshtml = "./contact_thx.html";				# �T���L���[��ʗpHTML
$errorhtml = "./contact_error.html";				# �G���[��ʗpHTML
$mailfile = "./thanksmail.txt";					# �T���L���[���[�����^
$mailstaff = "./mail2staff.txt";					# �N���C�A���g���[�����^

$twoBytes = '(?:[\x8E\xA1-\xFE][\xA1-\xFE])';	# ���p�Љ����ƑS�p����
$katakana = '(?:\xA5[\xA1-\xF6])';				# �@�`��(�J�^�J�i)
$kanji    = '(?:[\xB0-\xFE][\xA1-\xFE])';			# ����
$number = '(?:[\x30-\x39])'; 					# ���p����
$zuletter = '(?:[\x41-\x5a])'; 					# ���p�p�啶��

$bound = 'wq5se3d1ewabcdefg12345';


@messages = (
	' ���L���ł��B',
	' ���I���ł��B',
	' �L���͂ł��܂���B',
	' �I���͂R�ȓ��ł��肢���܂��B',
	' ���p�����ł��L���肢�܂��B',
	' ���͕������������܂��B',
	' �S�p�����ł��L���肢�܂��B',
	' �S�p�J�i�ł��L���肢�܂��B',
	' ���[���A�h���X�͐��m�ɂ��肢���܂��B',
	' �X�֔ԍ��͐��m�ɂ��肢���܂��B',
	' �d�b�ԍ��͐��m�ɂ��肢���܂��B',
	' Fax�ԍ��͐��m�ɂ��肢���܂��B',
	' �g�єԍ��͐��m�ɂ��肢���܂��B',
	' ���N�����͐��m�ɂ��肢���܂��B',
	' ����]�̍u�`���`�F�b�N���Ă��������B',
	' ID�����L�����Ă��������B',
	' ���t���ł��B',
	' 10���斢���B'
);	# �G���[���b�Z�[�W



# ���₢���킹�̍���
# %aryOtoiawase = (
#  '1', '�A���o���⃉�C�u�Ɋւ��邨�₢���킹',
#  '2', '�o���̂��˗�',
#  '3', '���̑�'
# );


@check_grp1 = (
'_Name',
'_Email',
'_Etc'
);	# �K�{���̓`�F�b�N


# ======================================================
# ���C��
# ======================================================

# ------------------------------------------------------
# �����̓��t�擾
($g_sec,$g_min,$g_hour,$g_day,$g_mon,$g_year,$g_wday,$g_yday,$g_isdst) = localtime(time);
$g_mon++;
$g_year += 1900;
$g_year = substr("0000$g_year",-4);
$g_mon = substr("00$g_mon",-2);
$g_day = substr("00$g_day",-2);
$g_today = "$g_year/$g_mon/$g_day\n";
@w = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
$date_now = sprintf("%04d\/%02d\/%02d(%s) %02d\:%02d",$g_year,$g_mon,$g_day,$w[$g_wday],$g_hour,$g_min);

# �p�����[�^�擾
$ret = &ReadParse;

if ($ret == 0) { &fatal_error('Data Empty:�f�[�^���͂�����܂���.'); }

# ------------------------------------------------------
# ���Ԃ��ۏ؂����z��Ɋi�[
foreach $data (@in) {
	$data =~ s/\+/ /g; # +���X�y�[�X�ɕϊ�
	($key,$val) = split(/=/,$data,2); # =�Ńt�H�[�����Ɠ��e�̕���
	$key =~ s/%([A-Fa-f0-9]{2})/pack("c",hex($1))/ge; # �t�H�[�������f�R�[�h
	push(@name,$key);
}


# ------------------------------------------------------
# �t�H�[���f�[�^�ҏW
foreach $name (@name) {
	($name, $filename) = split("\0", $name); # �k���R�[�h�ŕ���
	my $num = 0;
	my $lastspc = 0;
	foreach $value (split("\0", $in{$name})) { # �k���R�[�h�ŕ���
		if (!exists $out{$name}{$num}) { # �������O�̃f�[�^�Ɋi�[�ꏊ��p��
			$lastspc = 1; # �󗓂łȂ��t���O
			if ($name =~ /^_indispen$/i) { # ���e���R�}���h���̋��
				$indispen{$value} = 1; # �t���O�����Ƌ󗓂͑ʖ�
				next;
			}
			elsif ($name =~ /^_(.*)$/i) {  # _indispen�ȊO�̃R�}���h
				$cmd = "\_$1"; $check{$cmd} = $value; next;
			}
			push(@out, "$name\0$value"); # @out�ɒǉ�
			$out{$name}{$num} = $value;
			last; # ���[�v�̏I��
		}
		$num++;
	}
	if (!$lastspc) { # �f�[�^����̎��̏���
		if ($name =~ /^_(.*)$/) { next; }
		push(@out, $name);
	}
}

# ------------------------------------------------------
# �����R�[�h�̓���(s-jis)
foreach (@out) {
	($name,$value) = split("\0");
	&jcode::convert(*name,'sjis');
	&jcode::convert(*value,'sjis');		# SJIS�ɕϊ�
}

foreach $key(keys %out){
	foreach $value(keys %{$out{$key}}){
		$out{$key}{$value} =~ s/\x0D\x0A|\x0D|\x0A/\n/g; 	# ���s�R�[�h�̓���
		$out{$key}{$value} =~ s/\n//g;  		# ���s�R�[�h����
		$out{$key}{$value} =~ s/\t+//g; 		# �^�u������
		$out{$key}{$value} =~ s/\xA1\xA1|\x81\x40|\s//g;	# �󔒂�����
		&jcode'h2z_sjis(\$out{$key}{$value});	# ���p�J�i��S�p�J�i�ɕϊ�
	}
}

# ------------------------------------------------------
undef %errors;
if ($check{'_check'}) {
	# ���͍��ڃ`�F�b�N
	&check_proc;
	if (%errors) { 
		# �G���[�̕\��
                #&error_disp_proc;
		&error_proc; 
	} else {
		# step1 : ���e�m�F����
		&content_confirm_proc;
	}
}
else {
# step2 : �\���҂�E���[���A�h���X�擾
	$EMAIL = $out{'E-mail'}{'0'};

# step3 : ���[�����M����(�N���C�A���g����)
	&send_mail_proc;

# step4 : ���[�����M����(�����҈��Ċm�F���[���j
	&recept_mail_proc;

# step5 : �T���L���[HTML�\��
	&thanks_print_proc;

}
##
### END OF MAIN ###


# ======================================================
# �T�u���[�`��
# ======================================================
# ------------------------------------------------------
# ���e�m�F����
# ------------------------------------------------------
sub content_confirm_proc {
	# HTML TAG�ϊ�
	foreach $key(keys %out){
		foreach $value(keys %{$out{$key}}){
			$out{$key}{$value} =~ s/&/&amp;/g;
			$out{$key}{$value} =~ s/"/&quot;/g;
			$out{$key}{$value} =~ s/</&lt;/g;
			$out{$key}{$value} =~ s/>/&gt;/g;
		}
	}

	if (!open(HTML,"$kakuninhtml")) {
		&fatal_error("ReadFileOpenError: kakuninhtml($kakuninhtml)");
	} # �t�@�C�����J��
	my @msg = <HTML>;
	close (HTML);
	$msg = join('',@msg);

	# ���[�����M�p�B���̈�֒l��n��

        #��]���ڂ̕��͂����Ȃ��� reg_msg�@�֑���B�e�L�X�g���͂�()�ŕ\���B
	$msg =~ s/_#Name/$out{$in{'_Name'}}{'0'}/g;
	$msg =~ s/_#Company/$out{$in{'_Company'}}{'0'}/g;
	$msg =~ s/_#Email/$out{$in{'_Email'}}{'0'}/g;
	$msg =~ s/_#Item/$out{$in{'_Item'}}{'0'}/g;
	$msg =~ s/_#Etc/$out{$in{'_Etc'}}{'0'}/g;


	# HTML�\���p�̒l��n��
	print "Content-type:text/html; charset=\"Shift-JIS\"\n\n";
	print $msg;

}

# ------------------------------------------------------
# �G���[�\������
# ------------------------------------------------------
sub error_disp_proc {

    print "Content-type:text/html; charset=\"Shift-JIS\"\n\n";
    print "<html><head><title>error disp</title></head><body>";

    foreach (($k, $v) = each(errors)) {
    	print "$k=$v<br>";
    }

    print "----------------------<br>";
    foreach $n (@name) {
	print "$n => \"$errors{$n}\"<br>";
    }
    print "</html>";
    return 0;
}

sub error_proc {

	if (!open(HTML,"$errorhtml")) {
		&fatal_error("ReadFileOpenError: errorhtml($errorhtml)");
	} # ���^HTML�t�@�C�����J��
	my @msg = <HTML>;
	close (HTML);

	$msg = join('',@msg);

	$msg =~ s/_#Name/$out{$in{'_Name'}}{'0'}/g;
	$msg =~ s/_#Company/$out{$in{'_Company'}}{'0'}/g;
	$msg =~ s/_#Email/$out{$in{'_Email'}}{'0'}/g;
	$msg =~ s/_#Item/$out{$in{'_Item'}}{'0'}/g;
	$msg =~ s/_#Etc/$out{$in{'_Etc'}}{'0'}/g;



	$msg =~ s/_#NamError/$errors{$in{'_Name'}}/;
	$msg =~ s/_#CompError/$errors{$in{'_Company'}}/;
	$msg =~ s/_#EmError/$errors{$in{'_Email'}}/;
	$msg =~ s/_#ItError/$errors{$in{'_Item'}}/;
	$msg =~ s/_#EtError/$errors{$in{'_Etc'}}/;

	print "Content-type:text/html; charset=\"Shift-JIS\"\n\n";
	print $msg;

}

# ------------------------------------------------------
# �S�p�`�F�b�N(�⏕�������Ή�)(EUC)
# ------------------------------------------------------
sub check_twobyte {
	my $test_word = shift;
	1 while $test_word =~ s/^([\x8E\xA1-\xFE][\xA1-\xFE]|\x8F[\xA1-\xFE][\xA1-\xFE]|\s)//;
	($test_word ? 0 : 1);
}

# ------------------------------------------------------
# �J�^�J�i�`�F�b�N(�S�p�����A�u�E�v��OK)(EUC)
# ------------------------------------------------------
sub check_katakana {
	my $test_word = shift;
	if( $test_word =~ /^(\x81\x7c|\x81\x5b)/ ||
	$test_word =~ /(\x81\x7c|\x81\x5b){2,}/ ){
		return 0;
	}
	1 while $test_word =~ s/^(\xA5[\xA1-\xF6]|\xA1\xA1|\xA1\xBC|\xA1\xDD|\xA3[\xB0-\xB9]|\xA3[\xB0-\xB9]|[\xA1\xA6]|\x8E[\xA6-\xDF]|\s)//;
	($test_word ? 0 : 1);
}

# ------------------------------------------------------
# �����`�F�b�N(EUC)
# ------------------------------------------------------
sub check_kanji {
	my $test_word = shift;
	if( $test_word =~ /^(\x81\x7c|\x81\x5b)/ ||
	$test_word =~ /(\x81\x7c|\x81\x5b){2,}/ ){
		return 0;
	}
	1 while $test_word =~ s/^([\xB0-\xFE][\xA1-\xFE]|\xA1\xA1|\xA1\xBC|\xA1\xDD|\s)//;
	($test_word ? 0 : 1);
}

# ------------------------------------------------------
# ���p�`�F�b�N
# ------------------------------------------------------
sub check_han {
	my $test_word = shift;
	1 while $test_word =~ s/^([\x00-\x7F])//;
	($test_word ? 0 : 1);
}

# ------------------------------------------------------
# ���p�p�啶�������`?�N
# ------------------------------------------------------
sub check_zuletter {
	my $test_word = shift;
	1 while $test_word =~ s/^([\x30-\x39]|[\x41-\x5a])//;
	($test_word ? 0 : 1);
}

# ------------------------------------------------------
# ���p�����`�F�b�N
# ------------------------------------------------------
sub check_hannum {
	my $test_word = shift;
	1 while $test_word =~ s/^([\x30-\x39])//;
	($test_word ? 0 : 1);
}
# ------------------------------------------------------
# ���p�S�p�󔒒u������
# ------------------------------------------------------
sub conv_space {
	my $test_word = shift;
	$test_word =~ s/\xA1\xA1|\s|\x81\x40//g;			# �󔒂�����
	return $test_word;
}

# ------------------------------------------------------
# ���ꕶ���u������(NEC �I�� IBM �g�������R�[�h,IBM �g�������R�[�h)(sjis)
# ------------------------------------------------------
sub conv_sp_sjis {
	my $test_word = shift;
	$test_word =~ s/[\xED-\xEE][\x40-\xFC]|[\xFA-\xFC][\x40-\xFC]//g;	# ��������
	return $test_word;
}

# ------------------------------------------------------
# ���t�̑��݃`�F�b�N
# ------------------------------------------------------
sub DateExists {
	my($year, $mon, $day) = @_;
	if ($year eq '' && $mon eq '' && $day eq '') {return 1;}
	eval {timelocal(0, 0, 0, $day, $mon-1, $year-1900);};
	if($@) {return "0";}
	if($mon == 12) {$mon = 0;}
	my $time = timelocal(0, 0, 0, 1, $mon, $year-1900);
	$time -= 60*60*24;
	my @date = localtime($time);
	if($day > $date[3]) {return 0;}
	return 1; # normal
}

# ------------------------------------------------------
# ����t�`�F�b�N�i�{10���ȏ�j
# ------------------------------------------------------
sub DateCheck {
	my($year, $mon, $day) = @_;
	my($hours, $min, $sec) = 0;
	my $time_test = timelocal($sec, $min, $hours, $day, $mon - 1, $year);
	my $time_now = timelocal($sec, $min, $hours, $g_day, $g_mon - 1, $g_year);
	my $time_offset = 864000;  # = 60�b x 60�� x 24���� x 10��
	if ($time_test < ($time_now + $time_offset)) {
		return 0; # error
	}
	return 1; #normal
}

# ------------------------------------------------------
# ���[�����M����(�V�X�e��==>�N���C�A���g����)
# ------------------------------------------------------
sub send_mail_proc {

	if (!open(MAIL,"$mailstaff")) {
		&fatal_error("ReadFileOpenError: mailstaff($mailstaff)");
	} # �t�@�C�����J��
	my @msg = <MAIL>;
	close (MAIL);

	$msg = join('',@msg);	# ������

	if (!open(OUT,"|$nkf -j | $sendmail -t ")) { &fatal_error('sendmail: PIPE Error'); }

	$host = $ENV{'REMOTE_HOST'}; # �����[�g�z�X�g���擾
	$addr = $ENV{'REMOTE_ADDR'};
	if ($host eq '') { $host = $addr; }
	if ($host eq $addr) { $host = gethostbyaddr(pack('C4',split(/\./,$host)),2) || $addr; }

    # ���[���̏�Ԃ��������
	print OUT "X-Processed: $date_now\n";
	print OUT "X-Mailer: MAIL AGENT v1.00 by gardensakura.com\n";
	print OUT "X-HTTP_REFERER: $ref\n";
	print OUT "X-HTTP-User-Agent: $ENV{'HTTP_USER_AGENT'}\n";
	print OUT "X-Remote-host: $host\n";
	print OUT "X-Remote-Addr: $ENV{'REMOTE_ADDR'}\n";
	print OUT "To: $mailto\n";
	print OUT "From: $EMAIL\n";
	print OUT "Subject: $title\n";
	# print OUT "Reply-to: $CFG_REPLYTO\n";
	print OUT "Content-Transfer-Encoding: 7bit\n";
	print OUT "Content-Type: text/plain; charset=ISO-2022-JP\n";
	print OUT "\n";

	$msg =~ s/_#Name/$out{'�����O'}{'0'}/;
	$msg =~ s/_#Company/$out{'��Ж�'}{'0'}/;
	$msg =~ s/_#Email/$out{'E-mail'}{'0'}/;
	$msg =~ s/_#Item/$out{'���₢��������'}{'0'}/;
	$msg =~ s/_#Etc/$out{'���₢�������e'}{'0'}/;


# ���[���{��
	print OUT "\n";
	print OUT "$msg\n";
	print OUT "\n";
	print OUT "----------------------------------------------------------------------\n";
	print OUT "Date  :$date_now\n";
	print OUT "Host  :$host\n";
	print OUT "Agent :$ENV{'HTTP_USER_AGENT'}\n";
	print OUT "----------------------------------------------------------------------\n";
	
#return 0;
	close(OUT);
}


# ------------------------------------------------------
# ���[�����M����(������==>�����҈���)
# ------------------------------------------------------
sub recept_mail_proc {

	# ���M�h���C�������݂��Ȃ��ƃG���[�ŗ�����̂�
	@domain = split(/\@/, $EMAIL);
	if ($#domain <= 0) { return 1 ; }
	$host = $domain[1];
	# MX���R�[�h���`�F�b�N
	$mx = get_mx($host);
	if ($mx < 0) { return 1; }

	#($name, $aliases, $addrtype, $length, @addrs) = gethostbyname($host);
	#if ($name eq '') { return 1; }

	if (!open(MAIL,"$mailfile")) {
		&fatal_error("ReadFileOpenError: thanksmail($mailfile)");
	} # �t�@�C�����J��
	my @msg = <MAIL>;
	close (MAIL);

	$msg = join('',@msg);	# ������

	$msg =~ s/_#Name/$out{'�����O'}{'0'}/;
	$msg =~ s/_#Company/$out{'��Ж�'}{'0'}/;
	$msg =~ s/_#Email/$out{'E-mail'}{'0'}/;
	$msg =~ s/_#Item/$out{'���₢��������'}{'0'}/;
	$msg =~ s/_#Etc/$out{'���₢�������e'}{'0'}/;


# ���[���J�n
	if (!open(OUT,"|$nkf -j | $sendmail -t ")) { &fatal_error('Recept_MailOpenError'); }

# ���[���w�b�_���
	print OUT "X-Processed: $date_now\n";
	print OUT "X-Mailer: MAIL AGENT v1.00 by gardensakura.com\n";
	print OUT "To: $EMAIL\n";			# ������
	print OUT "From: $CFG_REGMAIL\n";		# �N���C�A���g
	if ($CFG_BCC ne ''){
		print OUT "Bcc: $CFG_BCC\n";		# BCC
	}
	print OUT "Subject: $titlerep\n";			# �^�C�g��
	print OUT "Reply-to: $CFG_REPLYTO\n";		# Reply-to
	print OUT "Content-Transfer-Encoding: 7bit\n";
	print OUT "Content-Type: text/plain; charset=ISO-2022-JP\n";

# ���[���{��
	print OUT "\n";
	print OUT "$msg\n";

	close (OUT);
}


# ------------------------------------------------------
# �T���L���[HTML�\������
# ------------------------------------------------------
sub thanks_print_proc {

	if (!open(HTML,"$thankshtml")) {
		&fatal_error("ReadFileOpenError: thankshtml($thankshtml)");
	} # ���^HTML�t�@�C�����J��
	my @msg = <HTML>;
	close (HTML);

	$msg = join('',@msg);

	print "Content-type:text/html; charset=\"Shift-JIS\"\n\n";
	print $msg;

}

# ------------------------------------------------------
# �v���I�G���[����
# ------------------------------------------------------
sub fatal_error {
	my $err_msg = shift;
	&CgiDie($err_msg);
}

# ------------------------------------------------------
# ���e�`�F�b�N
# ------------------------------------------------------
sub check_proc {

	# �K�{���̓`�F�b�N
	foreach $item (@check_grp1) {
		if (&conv_space($in{$in{$item}}) eq '') { 
			%errors = (%errors, $in{$item}, $messages[0]);	# ���L��
		}
	}

		# ���[���A�h���X
	if (!exists $errors{$in{'_Email'}}) {
		$t_chk = &conv_space($in{$in{'_Email'}});
		if ($t_chk ne '') { 
			if (length $t_chk > 100) { # 
				%errors = (%errors, $in{'_Email'}, $messages[8]);
			}
			if ($t_chk =~ /\s|\,/) { 
				%errors = (%errors, $in{'_Email'}, $messages[8]);
			}
			else {
				unless ($t_chk =~ /\b[-\w.]+@[-\w.]+\.[-\w]+\b/) { 
					%errors = (%errors, $in{'_Email'}, $messages[8]);
				}
			}
			if (!&check_han($t_chk)){
				%errors = (%errors, $in{'_Email'}, $messages[8]);
			}
		}
	}


# �G���[�`�F�b�N

		# �X�֔ԍ�
	if (!exists $errors{$in{'_Yubin'}}) {
		$t_chk = &conv_space($in{$in{'_Yubin'}});
		if ($t_chk =~ /[^0-9\-]/) { 
				%errors = (%errors, $in{'_Yubin'}, $messages[9]);
	}
}

		# �d�b�ԍ�
	if (!exists $errors{$in{'_Tel'}}) {
		$t_chk = &conv_space($in{$in{'_Tel'}});
		if ($t_chk =~ /[^0-9\-]/) { 
				%errors = (%errors, $in{'_Tel'}, $messages[10]);
	}
}



}

#-----------------------------
# �`�F�b�N�{�b�N�X�̒l���擾
#-----------------------------
sub getCheckBox {
    *input_ary = @_[0];
    *output_ary = @_[1];
    $var_name = @_[2];
    foreach (@input_ary) {
	($name,$value) = split("\0");
	if ($name eq $var_name) {
	    push(output_ary, $value);
	}
    }
    return 0;
}

############## MX(���[���T�[�o)�̒��ו� ####################
sub get_cmd {
	local($c) = @_;
	local($a,$b);
	foreach $a ('','/usr','/usr/local') {
		foreach $b ('/bin/','/sbin/') {
			return "$a$b$c" if (-x "$a$b$c");
		}
	}
}
sub get_mx {
	local($host) = @_;
	local($nslookup,@mx);
	$nslookup = get_cmd('nslookup') || return;
	open(FH,"$nslookup -type=MX $host |") || return;
	while(<FH>) {
		next unless /=/; # ���ʂ������s
		chop; split;
		push(@mx,pop(@_)); # �󔒂ŋ�؂�������
	}
	close(FH);
	@mx;
}

# ------------------------------------------------------
### END ###
# ------------------------------------------------------
