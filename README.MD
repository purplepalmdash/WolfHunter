### Purpose Of WolfHunter
Recently I am using Cobbler and Ansible for deploying Cloudstack On CentOS, these 2 tools are powerful and they could fulfill my requirement for deploying Cloudstack automatically, but the business team may need a much more simple yet powerful tool(With UI) for deploying the products in production environment. So I begin to write WolfHunter, for simply use a web based UI for managing the deployment.     

### Dependency
Cobbler Server runs on CentOS 6.6.     
Ansible.    
Bottle.     

For installing Bottle:    

```
$ sudo yum -y install python-pip
$ pip install bottle
```

The id_pub.rsa should be inserted into the deployed system, thus we could combine the operation together with Cobbler and Ansible.   
