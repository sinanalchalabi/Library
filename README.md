##Libararies Application
This is a project to list libraries with its books and info about books

###Requirement
1-Vagrant and VirtualBox
2-Source Code

####Terminal
If you are using a Mac or Linux system,
your regular terminal program will do just fine. 
On Windows, we recommend using the Git Bash
terminal that comes with the Git software. 
If you don't already have Git installed,
download Git from git-scm.com.

####Installing the Virtual Machine
We'll use a virtual machine (VM)
to run an SQL database server and a web app that uses it. 
The VM is a Linux server system that runs on top of your own computer. 
You can share files easily between your computer and the VM; 
and you'll be running a web service inside the VM
which you'll be able to access from your regular browser.
We're using tools called Vagrant and VirtualBox to install and manage the VM.

####Install VirtualBox
VirtualBox is the software that actually runs the virtual machine.
You can download it from virtualbox.org.
Install the platform package for your operating system.
You do not need the extension pack or the SDK. 
You do not need to launch VirtualBox after installing it;
Vagrant will do that.

####Install Vagrant
Vagrant is the software that configures the VM and lets you share files
between your host computer and the VM's filesystem.
Download it from vagrantup.com. 
Install the version for your operating system.
Windows users: The Installer may ask you to grant network permissions
to Vagrant or make a firewall exception. Be sure to allow this.

####Download the VM configuration
There are a couple of different ways you can download the VM configuration.
You can download and unzip this file: FSND-Virtual-Machine.zip 
This will give you a directory called FSND-Virtual-Machine.
It may be located inside your Downloads folder.
Alternately, you can use Github to fork and clone the repository:
https://github.com/udacity/fullstack-nanodegree-vm.
Either way, you will end up with a new directory containing the VM files.
Change to this directory in your terminal with cd.
Inside, you will find another directory called vagrant.
Change directory to the vagrant directory.

#####Start the virtual machine
From your terminal, inside the vagrant subdirectory,
run the command vagrant up.
This will cause Vagrant to download the 
Linux operating system and install it.
This may take quite a while (many minutes)
depending on how fast your Internet connection is.
When vagrant up is finished running, you will get your shell prompt back.
At this point, you can run vagrant ssh to log in
to your newly installed Linux VM

####Run the database_setup.py from terminal
`python database_setup.py`
if you want to dump some data then running
`python randomData.py`

###Usage
After compeleting the requirements,
you can easily run the code in new terminal:
`python project.py`
then go to the internet explorer and type:
`http://localhost:8000`
to access API Endpoints :
`http://localhost:8000/library.json`
to access specific book info :
`http://localhost:8000/book/ID/JOSN`
(put the ID of the book instead of "ID"
###Features
1-Any one can survey all the libraries and books
2-Only authrized users can (add,edit or delete) data from the database
3-Third party login (Google)
4-API Endpoints

###License:
It is a free to use and redistribute.