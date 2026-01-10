#!/usr/bin/env bash

function print_help() {
    echo "Usage: $(basename "$0") [options...] <address>"
    echo " -a, --address    Set UMS or ICG server FQDN Address"
    echo " -p, --port       Set UMS or ICG Port (Default 8443)"
    echo " -o, --output     Set the output file if you wish to save it"
    echo " -h, --help       Print this message"
    echo
    exit 0
}

function fecho() {
    #######################################
    # Formatted echo responses
    # Globals:
    #   None
    # Arguments
    #   colors
    #       -re     red text
    #       -gr     green text
    #       -ye     yellow text
    #       -bl     blue text
    #   pass or fail
    #       -p      pass
    #       -f      fail
    # Output
    #   Standard Out formatted  text
    #######################################

    local text="${!#}"

    if [ -n "$output" ]; then
        echo "$text" >> "$output"
    fi
    

    while (($# > 1)); do
        key=$1
        case "$key" in
            "-re")
                textc="\033[0;31m$text\033[0m"
                shift
                ;;
            "-gr")  
                textc="\033[0;32m$text\033[0m"
                shift
                ;; 
            "-ye")
                textc="\033[1;33m$text\033[0m"
                shift 
                ;; 
            "-bl") 
                textc="\033[0;34m$text\033[0m"
                shift
                ;; 
            "-p")   
                pf="[\033[0;32m\xE2\x9C\x94\033[0m]"
                shift
                ;; 
            "-f")
                pf="[\033[0;31mX\033[0m]"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    # Combine output as needed
    if [ -z "$textc" ]; then
        textc="$text"
    fi

    if [ ! -z $pf ]; then
        textc="$pf $textc"
    fi

    echo -e "$textc"

    # Reset locals and return
    unset textc pf    
    return 0
}

function web_connect(){
    
    # Default Params
    tls=true
    proto="https"
    tlsv="1.3"
    timeout=5
    maxTime=5
    validate=false
    silent=true

    curlArgs=""

    while (($# > 1)); do
        key=$1
        case "$key" in
            "--host"|"-h")
                host="$2"
                shift 2
                ;;
            "--port"|"-p")
                port="$2"
                shift 2
                ;;
            "--path"|"-pa")
                path="$2"
                shift 2
                ;;
            "--notls"|"-nt")
                tls=false
                proto="http"
                shift
                ;;
            "--validate")
                validate=true
                shift
                ;;
            "--versbose"|"-v")
                silent=false
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [ $port == "" ]; then # Default to UMS / ICG Port
        port=8443
    fi

    curlArgs="--connect-timeout ${timeout} --max-time ${maxTime}"

    if [ $silent == true ]; then # Set to silent and disable progress bars
        curlArgs="$curlArgs --silent"
    fi

    if [ $tls == true ]; then # TLS and certificate validation if https
        curlArgs="$curlArgs --tlsv${tlsv}"
        if [ $validate == false ]; then
            curlArgs="$curlArgs --insecure"
        fi
    fi

    local url="${proto}://${host}:${port}/${path}" # Build the path

    curl ${curlArgs} ${url} # Call curl
    
    
}



## Script Functions

function env_check(){
    isRoot=false
    hasRScan=false
    isIGEL=false
    hasPPort=false
    hasNC=false
    hasNMAP=false

    if [ "$(id -u)" -eq 0 ]; then
        fecho -p "Running as root."
        isRoot=true
    else
        fecho -f "Not running as root, scanning will be limited"
    fi
    
    if which rustscan >/dev/null 2>&1; then
        fecho -p "rustscan found"
        hasRScan=true
    else
        fecho -f "rustscan not found"
    fi

    if which nmap >/dev/null 2>&1; then
        fecho -p "nmap found"
        hasNMAP=true
        return 0
    else
        fecho -f "nmap not found"
    fi


    if which nc >/dev/null 2>&1; then
        fecho -p "NetCan (nc) found"
        hasNC=true
    else
        fecho -f "NetCat (nc) not found"
    fi

    if which probeport >/dev/null 2>&1; then
        fecho -p "Probeport Found"
        isIGEL=true
        hasPPort=true
    else
        fecho -f "Probeport not found"
    fi
}

function ums_test() {
    fecho ""
    fecho -ye "Starting ${srvType} Specific Tests"
    fecho     '============================'

    fecho -bl 'OS 12 Management'
    fecho     '----------------'
    if dig +short -x "${srvIP}" | grep -q "${srvAddr}"; then
        fecho -p "Reverse Lookup for $srvIP --> $srvAddr: Pass"
    else
        fecho -f -re "Reverse Lookup for $srvIP --> $srvAddr: Fail"
    fi
    fecho ""
    fecho -bl 'Automatic Registration Validation'
    fecho     '---------------------------------'

    rmserverIP=( `dig +short igelrmserver.${srvDomain}` )

    if [ -n "${rmserverIP}" ]; then
        fecho -p "igelrmserver FQDN resolved"
    else
        fecho -p "igelrmserver FQDN cannot be resolved"
    fi

    if dig +short igelrmserver; then
        fecho -p "igelrmserver shortname resolved"
    else
        fecho -f "Cannot resolve igelrmserver via shortname"
    fi

    fecho ""

    local rlook=false

    if [ -n "$rmserverIP" ]; then
        for ip in ${rmserverIP[@]}; do
            fecho -p "igelrmserver IP: $ip"
            fecho "    - Reverse Lookup: `nslookup $ip | head -1| sed 's/.*name = //g'`"
        done
    fi

    # Check reverse IP of igelrmserver
    for ip in ${rmserverIP[@]}; do
        if dig +short -x ${ip} | tr '[:upper:]' '[:lower:]' | grep -q "${srvAddr}"; then
            fecho -p -gr "igelrmserver revers lookup to ${srvAddr}: Pass"
            rlook=true            
        fi
    done
    
    if [ "${rlook}" == "false" ]; then 
        fecho -f -re "Fail: igelrmserver IP does not resolve to ${srvAddr}"
    fi
}

function icg_test() {
    fecho ""
    fecho -ye "Starting ${srvType} Specific Tests"
    fecho     '============================='
    
    if which whois >/dev/null; then
        icgOrg=`whois ${srvIP} | grep  "OrgName" | sed 's/OrgName: *//g'`
    else
        fecho -ye "Warning, no "whois" found in path, attempting to get ${srvIP} via curl."
        icgOrg=`web_connect -s -h "whois.arin.net" -p 443 --path "rest/ip/${srvIP}.txt" | grep  "Organization" | sed 's/Organization: *//g'`
    fi

    
    fecho "  - Hosted by: $icgOrg"

    serverStatus=`web_connect -h "${srvAddr}" -p 8443 --path "${srvDir}/server-status" | sed 's/{\"startUpTime\":\"//g' | sed 's/[.].*//g'`

    fecho "  - ICG Startup Time: $serverStatus" 

}

## Global variables
#declare -r curlOpt=--silent --tlsv1.3 --insecure --connect-timeout 5 --max-time 5
declare -r ESTCert="./wumscert.p7b"
declare -r nmResult="/tmp/${srvAddr}_nmap.txt"
declare -r saved_IFS=$IFS

if [ -n "$output" ]; then 

    if [ -f $output ]; then
        rm -f $output
        
    fi

    touch $output
fi

srvAddr=${srvAddr,,}

rm -f "${ESTCert}"

reset

runtime=`date "+%Y.%m.%d @ %H:%M"`

fecho -bl 'IGEL Server Check'
fecho      '================='  
fecho "${runtime}"

fecho -ye 'Starting Environment Check'
env_check

fecho ""

# Capture arguments
if (( $# > 0 )); then

    while (($# > 0)); do
        key="$1"
        case $key in
            --address|-a)
                srvAddr="${2}"
                shift 2
                ;;
            --port|-p)
                srvPort="${2}"
                shift 2
                ;;
            --help|-h)
                print_help
                shift
                ;;
            --output|-o)
                output="$2"
                shift 2
                ;;
            *)
                srvAddr="$1"
                shift
                ;;
        esac
    done
else
    print_help
fi

srvDomain="${srvAddr#*.}"
srvHost=${srvAddr%%.*} 


if [ -z $srvPort ]; then 
    srvPort=8443
fi


fecho -ye "Checking Port ${srvPort} at ${srvAddr}"

PortCheck=false

if [ "${hasRScan}" ==  'true' ]; then
    if rustscan -a "${srvAddr}" -p "${srvPort}" >/dev/null 2>&1; then
        PortCheck=true
    fi


elif [ "${hasPPort}" == 'true' ]; then
    if probeport "${srvAddr}" "${srvPort}" >/dev/null 2>&1; then
        PortCheck=true
    fi

elif [ "${hasNC}" == 'true' ]; then
    if nc -z "${srvAddr}" "${srvPort}" >/dev/null 2>&1; then
        PortCheck=true
    fi
elif [ "${hasNMAP}" == 'true' ]; then
    if nmap ${srvAddr} -p ${srvPort} >/dev/null 2>&1; then
        PortCheck=true
    fi
else
    fecho -f -re "No tool found to validate port"
    PortCheck=warn

fi

if [ "${PortCheck}" == 'true' ]; then
    fecho -p "Port check pass"
    fecho ""
elif [ "${PortCheck}" == 'warn' ]; then
    fecho -f -re "No port check utility available"
else
    fecho -f -re "Cannot connect to ${srvAddr}:${srvPort}"
    fecho     "  - Do you need to specify a custom port?"
    fecho ""
    print_help
    exit 2
fi


fecho -ye "Retrieving Server Type"
if web_connect -h "${srvAddr}" -p ${srvPort} --path "usg/check-status" | grep -q '"status":'; then
    fecho -gr "UMS Server detected"
    srvType="ICG"
    srvDir='usg'
elif web_connect -h "${srvAddr}" -p ${srvPort} --path "ums/check-status" | grep -q '"status":'; then
    fecho -gr "UMS Server detected"
    srvType='UMS'
    srvDir='ums'
else
    fecho -f -re "No UMS or ICG Server Found"
    fecho ""
    exit 2
fi


fecho -p "${srvType} Found"

sleep 4

srvAddr="${srvAddr,,}"

reset
fecho ""
if [ "${srvType}" == "ICG" ]; then
    srvIP=`dig +short @1.1.1.1 ${srvAddr}`
else
    srvIP=`dig +short ${srvAddr}`
fi

fecho -ye "IGEL Server Check"
fecho      '==================='
fecho -bl "Testing: ${srvAddr} @ ${srvPort}"
fecho -bl "Server Type: ${srvType}"
fecho "  - ${srvType} Hostname: ${srvHost}"
fecho "  - ${srvType} Domain: ${srvDomain}"
fecho "  - ${srvType} IP Address: ${srvIP}"
fecho '-----------------------------'
fecho -p "Port is Open"

# ICG -  https://kb.igel.com/en/igel-cloud-gateway/current/how-to-monitor-the-igel-cloud-gateway#Monitoring_Possible_ICG_States
# UMS - https://kb.igel.com/en/universal-management-suite/current/how-to-check-the-current-state-of-the-igel-ums-ser

srvStatus=`web_connect -h ${srvAddr} -p ${srvPort} --path "${srvDir}/check-status"| sed 's/.*:"//g' | sed 's/\"\}//g'`



if [ "${srvStatus}" == "ok" ]; then
    fecho -p "${srvType} Status: ${srvStatus^^}"
elif [ -n "${srvStatus}" ]; then
    fecho -f "${srvType} Status: ${srvStatus^^}"
else 
    fecho -f "${srvType} status unknown!"
fi

if [ "${srvType}" == "ICG" ];then
    icg_test
elif [ "${srvType}" == "UMS" ];then
    ums_test
fi

fecho ""

fecho -ye "Starting Wider Network Scan"
fecho     '==========================='
if which nmap >/dev/null; then


    if [ "${isRoot}" != 'true' ]; then
        fecho -f "Not running as root!"
        fecho     "  - Attempting elevation"
        sudo nmap -O ${srvAddr} > "${nmResult}" && fecho -p "Elevation successful" ||  fecho -f "Elevation filed, continuing script"
        fecho ""
    else
        nmap -O ${srvAddr} > "${nmResult}"
        
    fi
else 
    fecho -f "No nmap Binary Found"
fi


if [ -f "${nmResult}" ]; then
    # Get OS Type
    osType="`cat "${nmResult}" | grep "OS details: "| sed 's/OS details: //g'`"
    nHops="`cat "${nmResult}" | grep 'Network Distance:' `"

    # Get ports
    IFS=$'\n'
    nPorts=( `cat "${nmResult}" | grep "/tcp\|/udp" | sed 's/open//g'` )

    if [ -n "$osType" ]; then
        fecho "Detected ${osType}"

    else
        fecho -f "Could not detect OS Type"
    fi

    if     [ -n "${nHops}" ]; then
        fecho "${nHops}"
    fi

    fecho "Open Ports"
    for p in ${nPorts[@]}; do
        fecho "- ${p}"
    done
    IFS=$saved_IFS
fi

fecho ""

fecho -ye 'Starting Certificate Validations'
fecho     '================================='

## EST Cert
#IFS=$'\n'
web_connect -h "${srvAddr}" -p ${srvPort} --path "device-connector/device/.well-known/est/cacerts" > "${ESTCert}"
#IFS=$saved_IFS

if  grep -qi "PKCS7" "${ESTCert}" ; then
    fecho -p "EST Certificate obtained"
else
    fecho -f "EST Cert cannot be obtained"
fi
fecho ""


## Public Cert
IFS=$'\n'
pubDNS=( `openssl s_client -connect ${srvAddr}:${srvPort} </dev/null 2>/dev/null| openssl x509 -noout -text | grep DNS: | sed 's/.*DNS://g'` )
pubIssuer=( `openssl s_client -connect ${srvAddr}:${srvPort} </dev/null 2>/dev/null| openssl x509 -noout -text | grep Issuer: | sed 's/Issuer://g'` )

#IFS=$saved_IFS


fecho -bl 'Endpoint Certificate Validation'
fecho     '-------------------------------'
fecho -bl 'Public Cert Valid Names'

for name in ${pubDNS[@]}; do
    fecho "  - ${name}"
done
fecho ""
fecho -bl 'Public Certificate Chain'
for ca in ${pubIssuer[@]}; do
    if fecho "${ca}" | grep -q "CN *=" ; then
        ca=`echo $ca| sed 's/^ *//'`
        fecho "  - ${ca}" 
    fi
done


ESTChain=( `openssl pkcs7 -in "${ESTCert}" -print_certs -text | grep "Subject" | grep "CN=" | awk '!seen[$0]++'` )

fecho ""
fecho -bl 'Device Trust (EST) Root Certificates'

for sub in ${ESTChain[@]}; do 
    sub=`echo ${sub} | sed 's/.*Subject: //g'`
    fecho "  - $sub"
done

rm -f "${ESTCert}"
rm -f "${nmResult}"
IFS=$saved_IFS

fecho 

exit