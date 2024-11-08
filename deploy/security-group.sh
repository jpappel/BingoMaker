aws ec2 create-security-group --group-name "bingo-maker-ec2" --description "Allow http(s), ssh, and database access" \
    --vpc-id "vpc-021dbf31759b3a397" \
    --tag-specifications '{"ResourceType":"security-group","Tags":[{"Key":"purpose","Value":"bingo-maker"},{"Key":"lifespan","Value":"indeterminate"}]}' 

aws ec2 authorize-security-group-ingress --group-id "sg-06a8b744eb03a0dd2" \
    --ip-permissions '{"FromPort":22,"ToPort":22,"IpProtocol":"tcp","IpRanges":[{"CidrIp":"0.0.0.0/0"}]}' '{"FromPort":80,"ToPort":80,"IpProtocol":"tcp","IpRanges":[{"CidrIp":"0.0.0.0/0"}]}' '{"FromPort":443,"ToPort":443,"IpProtocol":"tcp","IpRanges":[{"CidrIp":"0.0.0.0/0"}]}' 
