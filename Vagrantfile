# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = 'precise64'
  config.vm.host_name = 'dev'
  config.vm.box_url = 'http://files.vagrantup.com/precise64.box'

  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = 'vagrant/manifests'
  end

  config.vm.customize [
    'modifyvm', :id,
    '--memory', '512',
    '--name', 'Splunk STOMP',
  ]

  config.vm.forward_port 8000, 8000
  config.vm.forward_port 8089, 8089
end
