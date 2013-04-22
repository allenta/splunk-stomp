# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
  config.vm.box = 'precise64'
  config.vm.hostname = 'dev'
  config.vm.box_url = 'http://files.vagrantup.com/precise64.box'

  config.vm.provider :virtualbox do |vb|
    vb.customize [
      'modifyvm', :id,
      '--memory', '512',
      '--name', 'Splunk STOMP',
    ]
  end

  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = 'vagrant/manifests'
  end

  config.vm.network :forwarded_port, guest: 8000, host: 8000
  config.vm.network :forwarded_port, guest: 8089, host: 8089
  config.vm.network :forwarded_port, guest: 15672, host: 15672
  config.vm.network :forwarded_port, guest: 55672, host: 55672
end
