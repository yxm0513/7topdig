#!/usr/bin/perl
use Capture::Tiny qw(tee);
use File::Copy;
if($#ARGV < 0){
    print("usage: $0 host [ar].\n");
    exit(1);
}
my @ip;
my $sys;
my $cmd = '/c4shares/auto/devutils/bin/swarm ' . $ARGV[0];
print "CMD: " . $cmd . "\n";
my $out = `$cmd`;
if( $out=~ /Can't find system/){
   print "ERROR: Can't find system"  .  $ARGV[0]  . "\n";   
} else {
    if($out=~ /Lab IP SP[A|B]: ([\d\.]+)/g){
       push @ip, $1;    
    }
}

foreach my $ip (@ip){
    #if(system("ping -c 1 ". $ip . "2>&1 1>/dev/null") == 0 ){
    if(system("ping -c 1 ". $ip ) == 0 ){
        $sys = $ip;
    } else {
        print("ERROR: ". $ip . " is not pingable\n");   
    }
}
if ($sys){
    print "IP: " .$sys ."\n\n";
}else{
    print("ERROR: cannot get system ip\n");
    exit 1;    
}

$cmd = 'ssh -i /home/simon/public/keys/id_rsa.root -o "StrictHostKeyChecking no" root@' . $sys . ' svc_dc ';
print "CMD: " . $cmd . "\n";
$out = tee {system($cmd)};


if ($ARGV[1]){
    my $file;
    print $out;
    if($out =~ /to\s([\/\w_]+.*.tar)/g){
       $file = $1; 
    }else{
       print "NO file generated";
       exit 1;    
    }
    $ARGV[1] =~ s/^\s*//;
    $ARGV[1] =~ s/\s*$//;
    $cmd = "/c4shares/auto/devutils/bin//whereisAR $ARGV[1]";
    $out = `$cmd`;
    print "CMD: " . $cmd . "\n";
    if($out =~ /not found/){
      print $out;
      exit 1;     
    }else{
      $out =~ /([\/\d\w_-]+)/g;
      my $folder = $1;
      print "copy file $file to $folder";
      $cmd = 'scp -i /home/simon/public/keys/id_rsa.root -o "StrictHostKeyChecking no" root@' . $sys . ':'.$file . "  $folder";
      print "CMD: " . $cmd . "\n";
      $out = tee {system($cmd)};
    }
}
