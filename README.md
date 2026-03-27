# TUGAS1NETICS Laporan

## SOAL 1
```
Buatlah API publik dengan endpoint /health yang menampilkan informasi sebagai berikut:
CONTOH (value disesuaikan)
{
  "nama": "Sersan Mirai Afrizal",
  "nrp": "5025241999",
  "status": "UP",
  “timestamp”: time	// Current time
  "uptime": time		// Server uptime
}
Bahasa pemrograman dan teknologi yang digunakan dibebaskan kepada peserta.
```

```
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
from datetime import datetime, timezone, timedelta

# Record the start time
START_TIME = time.time()
# Set timezone to WIB (UTC+7)
WIB = timezone(timedelta(hours=7))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Strictly check that the path is exactly /health
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            uptime_seconds = time.time() - START_TIME
            
            response = {
                "nama": "Rendy Tanuwijaya",
                "nrp": "5025241099",
                "status": "UP",
                "timestamp": datetime.now(WIB).isoformat(),
                "uptime": f"{int(uptime_seconds)} seconds"
            }
            # Send the JSON payload
            self.wfile.write(json.dumps(response).encode())
        else:
            # Reject any other path like / or /test
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

# Start the server on port 8080
server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
print("Python API running on port 8080...")
server.serve_forever()
```

The code used in this server is python, it makes easier to force an only /health domain while leaving everything else as an error 404 not found
I believe the python code is rather self-explanatory and not in the spirit of the assignment so I shall skip explaining it.
The python code only really returns back the .json file required for the assignment

```
# Use a tiny Python image
FROM python:3.9-alpine

WORKDIR /app

# Copy your Python API script
COPY server.py .

EXPOSE 8080 # the port 8080

# Run the API
CMD ["python", "server.py"]
```
This is the Dockerfile to create the docker image
I then create the image by running
```
docker build -t my-health-api-py:v1 .
```

After checking that it works by using
```
docker run -p 8080:8080 my-health-api-py:v1
# and going to localhost:8080/health
```

I then upload it to artanisplays/my-health-api-py:v1 in the dockerhub
```
docker push artanisplays/my-health-api-py:v1
```
## SOAL 2
```
Lakukan deployment API tersebut di dalam container pada VPS publik. Gunakan port selain 80 dan 443 untuk menjalankan API.
```

I tried deploying it, but due to the shenanigans with Azure, I have decided not to fully complete this task.
Though there are some things word mentioning here

So the way this is supposed to go is that the Azure vm is supposed to host this API as a Public VPS and using terraform + Ansible to automate it

so using the main.tf, the commands are
```
terraform init
terraform apply
```
This then creates a VM to Azure via request locally, but due to a combination of Azure policies and Azure limitations added by Azure for students being weird.
It then becomes better to just create a vm directly on the Azure website. Then it gives a public ip and we're supposed to use this command
```
ansible-playbook -i "20.123.45.67," -u azureuser deploy.yml
```
Where the ip is an example if we got one

Then we can just do
```
curl http://20.123.45.67:8080/health
```
And it should've worked correctly
*should've...*


Anyways these are the short code explanations
```
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "API-Assignment-RG"
  # Change this line right here:
  location = "East Asia" 
}

resource "azurerm_virtual_network" "vnet" {
  name                = "api-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "subnet" {
  name                 = "api-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "public_ip" {
  name                = "api-public-ip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  
  # Change these two lines to use the modern Azure standard
  allocation_method   = "Static"
  sku                 = "Standard" 
}

resource "azurerm_network_security_group" "nsg" {
  name                = "api-nsg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "Nginx-Proxy-8080"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080" 
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface" "nic" {
  name                = "api-nic"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.public_ip.id
  }
}

resource "azurerm_network_interface_security_group_association" "nic_nsg" {
  network_interface_id      = azurerm_network_interface.nic.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

resource "azurerm_linux_virtual_machine" "vm" {
  name                = "public-api-vps"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  size                = "Standard_B1s"
  admin_username      = "azureuser"
  
  network_interface_ids = [azurerm_network_interface.nic.id]

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }
}

data "azurerm_public_ip" "get_ip" {
  name                = azurerm_public_ip.public_ip.name
  resource_group_name = azurerm_linux_virtual_machine.vm.resource_group_name
  depends_on          = [azurerm_linux_virtual_machine.vm]
}

output "server_public_ip" {
  value = data.azurerm_public_ip.get_ip.ip_address
}
```
This is the terraform code to get the azure vm working, starting from location, version, ubuntu version, even just os version, etc.


```
- name: Deploy API and Configure Nginx
  hosts: all
  become: yes
  vars:
    docker_image: "artanisplays/my-health-api-py:v1"

  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes

    - name: Install Docker and Nginx
      apt:
        name: 
          - docker.io
          - nginx
        state: present

    - name: Ensure Docker is running
      systemd:
        name: docker
        state: started
        enabled: yes

    - name: Pull the API Docker image
      command: docker pull {{ docker_image }}

    - name: Run the API container on internal port 9000
      command: >
        docker run -d 
        --name my-health-api 
        -p 9000:8080 
        --restart unless-stopped
        {{ docker_image }}

    - name: Deploy Nginx reverse proxy template
      template:
        src: api.conf.j2
        dest: /etc/nginx/sites-available/api.conf

    - name: Enable the Nginx configuration
      file:
        src: /etc/nginx/sites-available/api.conf
        dest: /etc/nginx/sites-enabled/api.conf
        state: link

    - name: Remove the default Nginx configuration
      file:
        path: /etc/nginx/sites-enabled/default
        state: absent

    - name: Restart Nginx to apply changes
      systemd:
        name: nginx
        state: restarted
        enabled: yes
```
This is the .yml for the Ansible, I believe the names are self-explanatory.
The code is meant to download and set up a new fresh linux vm automatically