
<h1 align="center">NACM</h1>
<h2 align="center">Network Automation Configuration Management</h2>

Fitur NACM:
- **Routing**: Konfigurasi dasar routing static, dynamic OSPF, RIPv1, RIPv2, dan BGP
- **Vlan**: Konfigurasi vlan id 
- **Code Based**: Mengirimkan konfigurasi berbasis text ke perangkat tujuan
- **Backup**: Backup konfigurasi perangkat
- **Restore**: Restore konfigurasi perangkat
- **Setting**: Menambah dan menghapus konfigurasi vendor

___

# Instalasi
## Requirement
    python 3.5+
    virtualenv
    
## Quick start
    sudo su
    git clone https://github.com/rhezaaw/new-nacm-production.git
    cd new-nacm-production
    virtualenv -p python3 env
    source env/bin/activate
    pip3 install -r requirements.txt
    cd nacm
    python3 manage.py runserver 0.0.0.0:8000
    akses via browser <ip:8000>
 
 ## Readme
    Pastikan server dapat terhubung ke perangkat yang dituju (router,switch,dll)
    Pastikan perangkat tujuan (router,switch) menggunakan protokol SSH versi 2
    Untuk perangkat cisco aktifkan scp server "ip scp server enable"
 
___

#### 1. Main Page
![Image of index](https://drive.google.com/uc?export=view&id=1amb9qXStcDtTMD7m5bR4qF641OBTo5vd)

#### 2. Routing
![Image of routing](https://drive.google.com/uc?export=view&id=13R-27aBNIoTrQzTVfyAMYRbrCXbx4SP9)

#### 3. Backup
![Image of backup](https://drive.google.com/uc?export=view&id=1D3I5AnDnBeAHYkGX59mRVp4L7BydjmPa)

#### 4. Restore
![Image of vlan](https://drive.google.com/uc?export=view&id=1zVi9I7bCvJ6f4NUe3ooFPqNfoSLfh3we)

___

** Keperluan tugas akhir
rheza.adhyatmaka@gmail.com
