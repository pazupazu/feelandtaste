#!/usr/bin/perl
##!C:/Perl5.6/bin/Perl


require './regist.cfg';
require './jcode.pl';
require './cgi-lib.pl';
require './mimew.pl';
use Time::Local;

# ======================================================
# 初期設定
# ======================================================

$sendmail = $CFG_SENDMAIL;
$nkf = $CFG_NKF;
$mailto = $CFG_MAILTO;							# メールの宛先(クライアント)
$title    = 'お問い合わせがありました'; # メールのタイトル(クライアント宛)
$titlerep    = '【FEEL AND TASTE】お問い合せを受付けました'; # メールのタイトル(注文者宛)
$kakuninhtml = "./contact_check.html";				# 確認画面用HTML 
$thankshtml = "./contact_thx.html";				# サンキュー画面用HTML
$errorhtml = "./contact_error.html";				# エラー画面用HTML
$mailfile = "./thanksmail.txt";					# サンキューメール雛型
$mailstaff = "./mail2staff.txt";					# クライアントメール雛型

$twoBytes = '(?:[\x8E\xA1-\xFE][\xA1-\xFE])';	# 半角片仮名と全角文字
$katakana = '(?:\xA5[\xA1-\xF6])';				# ァ～ヶ(カタカナ)
$kanji    = '(?:[\xB0-\xFE][\xA1-\xFE])';			# 漢字
$number = '(?:[\x30-\x39])'; 					# 半角数字
$zuletter = '(?:[\x41-\x5a])'; 					# 半角英大文字

$bound = 'wq5se3d1ewabcdefg12345';


@messages = (
	' 未記入です。',
	' 未選択です。',
	' 記入はできません。',
	' 選択は３つ以内でお願いします。',
	' 半角数字でご記入願います。',
	' 入力文字が多すぎます。',
	' 全角漢字でご記入願います。',
	' 全角カナでご記入願います。',
	' メールアドレスは正確にお願いします。',
	' 郵便番号は正確にお願いします。',
	' 電話番号は正確にお願いします。',
	' Fax番号は正確にお願いします。',
	' 携帯番号は正確にお願いします。',
	' 生年月日は正確にお願いします。',
	' ご希望の講義をチェックしてください。',
	' ID数を記入してください。',
	' 日付誤りです。',
	' 10日先未満。'
);	# エラーメッセージ



# お問い合わせの項目
# %aryOtoiawase = (
#  '1', 'アルバムやライブに関するお問い合わせ',
#  '2', '出演のご依頼',
#  '3', 'その他'
# );


@check_grp1 = (
'_Name',
'_Email',
'_Etc'
);	# 必須入力チェック


# ======================================================
# メイン
# ======================================================

# ------------------------------------------------------
# 今日の日付取得
($g_sec,$g_min,$g_hour,$g_day,$g_mon,$g_year,$g_wday,$g_yday,$g_isdst) = localtime(time);
$g_mon++;
$g_year += 1900;
$g_year = substr("0000$g_year",-4);
$g_mon = substr("00$g_mon",-2);
$g_day = substr("00$g_day",-2);
$g_today = "$g_year/$g_mon/$g_day\n";
@w = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
$date_now = sprintf("%04d\/%02d\/%02d(%s) %02d\:%02d",$g_year,$g_mon,$g_day,$w[$g_wday],$g_hour,$g_min);

# パラメータ取得
$ret = &ReadParse;

if ($ret == 0) { &fatal_error('Data Empty:データ入力がありません.'); }

# ------------------------------------------------------
# 順番が保証される配列に格納
foreach $data (@in) {
	$data =~ s/\+/ /g; # +をスペースに変換
	($key,$val) = split(/=/,$data,2); # =でフォーム名と内容の分離
	$key =~ s/%([A-Fa-f0-9]{2})/pack("c",hex($1))/ge; # フォーム名をデコード
	push(@name,$key);
}


# ------------------------------------------------------
# フォームデータ編集
foreach $name (@name) {
	($name, $filename) = split("\0", $name); # ヌルコードで分離
	my $num = 0;
	my $lastspc = 0;
	foreach $value (split("\0", $in{$name})) { # ヌルコードで分離
		if (!exists $out{$name}{$num}) { # 同じ名前のデータに格納場所を用意
			$lastspc = 1; # 空欄でないフラグ
			if ($name =~ /^_indispen$/i) { # 内容かコマンドかの区別
				$indispen{$value} = 1; # フラグが立つと空欄は駄目
				next;
			}
			elsif ($name =~ /^_(.*)$/i) {  # _indispen以外のコマンド
				$cmd = "\_$1"; $check{$cmd} = $value; next;
			}
			push(@out, "$name\0$value"); # @outに追加
			$out{$name}{$num} = $value;
			last; # ループの終了
		}
		$num++;
	}
	if (!$lastspc) { # データが空の時の処理
		if ($name =~ /^_(.*)$/) { next; }
		push(@out, $name);
	}
}

# ------------------------------------------------------
# 文字コードの統一(s-jis)
foreach (@out) {
	($name,$value) = split("\0");
	&jcode::convert(*name,'sjis');
	&jcode::convert(*value,'sjis');		# SJISに変換
}

foreach $key(keys %out){
	foreach $value(keys %{$out{$key}}){
		$out{$key}{$value} =~ s/\x0D\x0A|\x0D|\x0A/\n/g; 	# 改行コードの統一
		$out{$key}{$value} =~ s/\n//g;  		# 改行コード消す
		$out{$key}{$value} =~ s/\t+//g; 		# タブを消す
		$out{$key}{$value} =~ s/\xA1\xA1|\x81\x40|\s//g;	# 空白を消す
		&jcode'h2z_sjis(\$out{$key}{$value});	# 半角カナを全角カナに変換
	}
}

# ------------------------------------------------------
undef %errors;
if ($check{'_check'}) {
	# 入力項目チェック
	&check_proc;
	if (%errors) { 
		# エラーの表示
                #&error_disp_proc;
		&error_proc; 
	} else {
		# step1 : 内容確認処理
		&content_confirm_proc;
	}
}
else {
# step2 : 申込者のEメールアドレス取得
	$EMAIL = $out{'E-mail'}{'0'};

# step3 : メール送信処理(クライアント宛て)
	&send_mail_proc;

# step4 : メール送信処理(注文者宛て確認メール）
	&recept_mail_proc;

# step5 : サンキューHTML表示
	&thanks_print_proc;

}
##
### END OF MAIN ###


# ======================================================
# サブルーチン
# ======================================================
# ------------------------------------------------------
# 内容確認処理
# ------------------------------------------------------
sub content_confirm_proc {
	# HTML TAG変換
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
	} # ファイルを開く
	my @msg = <HTML>;
	close (HTML);
	$msg = join('',@msg);

	# メール送信用隠し領域へ値を渡す

        #希望項目の文章ををつなげて reg_msg　へ代入。テキスト入力も()で表示。
	$msg =~ s/_#Name/$out{$in{'_Name'}}{'0'}/g;
	$msg =~ s/_#Company/$out{$in{'_Company'}}{'0'}/g;
	$msg =~ s/_#Email/$out{$in{'_Email'}}{'0'}/g;
	$msg =~ s/_#Item/$out{$in{'_Item'}}{'0'}/g;
	$msg =~ s/_#Etc/$out{$in{'_Etc'}}{'0'}/g;


	# HTML表示用の値を渡す
	print "Content-type:text/html; charset=\"Shift-JIS\"\n\n";
	print $msg;

}

# ------------------------------------------------------
# エラー表示処理
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
	} # 雛型HTMLファイルを開く
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
# 全角チェック(補助漢字も対応)(EUC)
# ------------------------------------------------------
sub check_twobyte {
	my $test_word = shift;
	1 while $test_word =~ s/^([\x8E\xA1-\xFE][\xA1-\xFE]|\x8F[\xA1-\xFE][\xA1-\xFE]|\s)//;
	($test_word ? 0 : 1);
}

# ------------------------------------------------------
# カタカナチェック(全角数字、「・」もOK)(EUC)
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
# 漢字チェック(EUC)
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
# 半角チェック
# ------------------------------------------------------
sub check_han {
	my $test_word = shift;
	1 while $test_word =~ s/^([\x00-\x7F])//;
	($test_word ? 0 : 1);
}

# ------------------------------------------------------
# 半角英大文字数字チ?ク
# ------------------------------------------------------
sub check_zuletter {
	my $test_word = shift;
	1 while $test_word =~ s/^([\x30-\x39]|[\x41-\x5a])//;
	($test_word ? 0 : 1);
}

# ------------------------------------------------------
# 半角数字チェック
# ------------------------------------------------------
sub check_hannum {
	my $test_word = shift;
	1 while $test_word =~ s/^([\x30-\x39])//;
	($test_word ? 0 : 1);
}
# ------------------------------------------------------
# 半角全角空白置換処理
# ------------------------------------------------------
sub conv_space {
	my $test_word = shift;
	$test_word =~ s/\xA1\xA1|\s|\x81\x40//g;			# 空白を消す
	return $test_word;
}

# ------------------------------------------------------
# 特殊文字置換処理(NEC 選定 IBM 拡張文字コード,IBM 拡張文字コード)(sjis)
# ------------------------------------------------------
sub conv_sp_sjis {
	my $test_word = shift;
	$test_word =~ s/[\xED-\xEE][\x40-\xFC]|[\xFA-\xFC][\x40-\xFC]//g;	# 消去する
	return $test_word;
}

# ------------------------------------------------------
# 日付の存在チェック
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
# 先日付チェック（＋10日以上）
# ------------------------------------------------------
sub DateCheck {
	my($year, $mon, $day) = @_;
	my($hours, $min, $sec) = 0;
	my $time_test = timelocal($sec, $min, $hours, $day, $mon - 1, $year);
	my $time_now = timelocal($sec, $min, $hours, $g_day, $g_mon - 1, $g_year);
	my $time_offset = 864000;  # = 60秒 x 60分 x 24時間 x 10日
	if ($time_test < ($time_now + $time_offset)) {
		return 0; # error
	}
	return 1; #normal
}

# ------------------------------------------------------
# メール送信処理(システム==>クライアント宛て)
# ------------------------------------------------------
sub send_mail_proc {

	if (!open(MAIL,"$mailstaff")) {
		&fatal_error("ReadFileOpenError: mailstaff($mailstaff)");
	} # ファイルを開く
	my @msg = <MAIL>;
	close (MAIL);

	$msg = join('',@msg);	# 初期化

	if (!open(OUT,"|$nkf -j | $sendmail -t ")) { &fatal_error('sendmail: PIPE Error'); }

	$host = $ENV{'REMOTE_HOST'}; # リモートホスト名取得
	$addr = $ENV{'REMOTE_ADDR'};
	if ($host eq '') { $host = $addr; }
	if ($host eq $addr) { $host = gethostbyaddr(pack('C4',split(/\./,$host)),2) || $addr; }

    # メールの状態を示す情報
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

	$msg =~ s/_#Name/$out{'お名前'}{'0'}/;
	$msg =~ s/_#Company/$out{'会社名'}{'0'}/;
	$msg =~ s/_#Email/$out{'E-mail'}{'0'}/;
	$msg =~ s/_#Item/$out{'お問い合せ項目'}{'0'}/;
	$msg =~ s/_#Etc/$out{'お問い合せ内容'}{'0'}/;


# メール本文
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
# メール送信処理(事務局==>注文者宛て)
# ------------------------------------------------------
sub recept_mail_proc {

	# 送信ドメインが存在しないとエラーで落ちるので
	@domain = split(/\@/, $EMAIL);
	if ($#domain <= 0) { return 1 ; }
	$host = $domain[1];
	# MXレコードをチェック
	$mx = get_mx($host);
	if ($mx < 0) { return 1; }

	#($name, $aliases, $addrtype, $length, @addrs) = gethostbyname($host);
	#if ($name eq '') { return 1; }

	if (!open(MAIL,"$mailfile")) {
		&fatal_error("ReadFileOpenError: thanksmail($mailfile)");
	} # ファイルを開く
	my @msg = <MAIL>;
	close (MAIL);

	$msg = join('',@msg);	# 初期化

	$msg =~ s/_#Name/$out{'お名前'}{'0'}/;
	$msg =~ s/_#Company/$out{'会社名'}{'0'}/;
	$msg =~ s/_#Email/$out{'E-mail'}{'0'}/;
	$msg =~ s/_#Item/$out{'お問い合せ項目'}{'0'}/;
	$msg =~ s/_#Etc/$out{'お問い合せ内容'}{'0'}/;


# メール開始
	if (!open(OUT,"|$nkf -j | $sendmail -t ")) { &fatal_error('Recept_MailOpenError'); }

# メールヘッダ情報
	print OUT "X-Processed: $date_now\n";
	print OUT "X-Mailer: MAIL AGENT v1.00 by gardensakura.com\n";
	print OUT "To: $EMAIL\n";			# 注文者
	print OUT "From: $CFG_REGMAIL\n";		# クライアント
	if ($CFG_BCC ne ''){
		print OUT "Bcc: $CFG_BCC\n";		# BCC
	}
	print OUT "Subject: $titlerep\n";			# タイトル
	print OUT "Reply-to: $CFG_REPLYTO\n";		# Reply-to
	print OUT "Content-Transfer-Encoding: 7bit\n";
	print OUT "Content-Type: text/plain; charset=ISO-2022-JP\n";

# メール本文
	print OUT "\n";
	print OUT "$msg\n";

	close (OUT);
}


# ------------------------------------------------------
# サンキューHTML表示処理
# ------------------------------------------------------
sub thanks_print_proc {

	if (!open(HTML,"$thankshtml")) {
		&fatal_error("ReadFileOpenError: thankshtml($thankshtml)");
	} # 雛型HTMLファイルを開く
	my @msg = <HTML>;
	close (HTML);

	$msg = join('',@msg);

	print "Content-type:text/html; charset=\"Shift-JIS\"\n\n";
	print $msg;

}

# ------------------------------------------------------
# 致命的エラー処理
# ------------------------------------------------------
sub fatal_error {
	my $err_msg = shift;
	&CgiDie($err_msg);
}

# ------------------------------------------------------
# 内容チェック
# ------------------------------------------------------
sub check_proc {

	# 必須入力チェック
	foreach $item (@check_grp1) {
		if (&conv_space($in{$in{$item}}) eq '') { 
			%errors = (%errors, $in{$item}, $messages[0]);	# 未記入
		}
	}

		# メールアドレス
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


# エラーチェック

		# 郵便番号
	if (!exists $errors{$in{'_Yubin'}}) {
		$t_chk = &conv_space($in{$in{'_Yubin'}});
		if ($t_chk =~ /[^0-9\-]/) { 
				%errors = (%errors, $in{'_Yubin'}, $messages[9]);
	}
}

		# 電話番号
	if (!exists $errors{$in{'_Tel'}}) {
		$t_chk = &conv_space($in{$in{'_Tel'}});
		if ($t_chk =~ /[^0-9\-]/) { 
				%errors = (%errors, $in{'_Tel'}, $messages[10]);
	}
}



}

#-----------------------------
# チェックボックスの値を取得
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

############## MX(メールサーバ)の調べ方 ####################
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
		next unless /=/; # 結果を示す行
		chop; split;
		push(@mx,pop(@_)); # 空白で区切った末尾
	}
	close(FH);
	@mx;
}

# ------------------------------------------------------
### END ###
# ------------------------------------------------------
