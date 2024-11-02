aws ec2 run-instances --image-id "ami-06b21ccaeff8cd686" --instance-type "t2.micro" \
    --key-name "vockey" --network-interfaces '{"AssociatePublicIpAddress":true,"DeviceIndex":0,"Groups":["sg-06a8b744eb03a0dd2"]}' \
    --credit-specification '{"CpuCredits":"standard"}' \
    --tag-specifications '{"ResourceType":"instance","Tags":[{"Key":"Name","Value":"bingo-maker"}]}' \
    --metadata-options '{"HttpEndpoint":"enabled","HttpPutResponseHopLimit":2,"HttpTokens":"required"}' \
    -private-dns-name-options '{"HostnameType":"ip-name","EnableResourceNameDnsARecord":true,"EnableResourceNameDnsAAAARecord":false}' \
    --user-data file://deploy/userdata.sh \
    --count "1" 
