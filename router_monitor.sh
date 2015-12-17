node_list_raw=$(bmx6 -c --originators)                                                                                                                                  
                                                                                                                                                                        
node_list_raw=$(printf "%s" "$node_list_raw" | sed -e "s/[[:space:]]\+/,/g")                                                                                            
node_list_raw=$(printf "%s" "$node_list_raw" | sed -e ':a;N;$!ba;s/\n/\\n/g')                                                                                           
                                                                                                                                                                        
node_list=$node_list_raw                                                                                                                                                
                                                                                                                                                                        
host="http://10.224.98.177:5000/api/v1/routerdata"                                                                                                                       
timestamp=$(date +%s)                                                                                                                                                   
                                                                                                                                                                        
data={\"nodes\":\"$node_list\",\"timestamp\":\"$timestamp\"}                                                                                                            
                                                                                                                                                                        
curl -i -X POST -H "Content-Type: application/json" -d "$data" $host
