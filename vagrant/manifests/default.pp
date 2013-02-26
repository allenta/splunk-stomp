class phase1 {
  exec {'apt-get-update':
    command => '/usr/bin/apt-get update'
  }

  package {['python', 'python-pip', 'rabbitmq-server', 'rabbitmq-stomp']:
    ensure => present,
    require => Exec['apt-get-update'],
  }
}

class phase2 {
  Class['phase1'] -> Class['phase2']

  package {['virtualenv']:
    ensure   => 'installed',
    provider => 'pip',
  }

  service {['rabbitmq-server']:
    enable => true,
    ensure => running,
  }

  exec {'create-virtualenv':
    creates => '/home/vagrant/.virtualenvs/splunkstomp/',
    user => 'vagrant',
    path => ['/bin', '/usr/bin', '/usr/local/bin'],
    command => 'mkdir -p /home/vagrant/.virtualenvs; virtualenv /home/vagrant/.virtualenvs/splunkstomp',
    require => Package['virtualenv'],
  }

  exec {'install-virtualenv-dependencies':
    path => ['/bin', '/usr/bin'],
    user => 'vagrant',
    provider => 'shell',
    command => '. /home/vagrant/.virtualenvs/splunkstomp/bin/activate; pip install stomp.py',
    require => Exec['create-virtualenv'],
  }

  file {'/home/vagrant/.profile':
    ensure => present,
    mode => 0644,
    owner => 'vagrant',
    group => 'vagrant',
    source => '/vagrant/vagrant/files/profile',
  }

  file {'/home/vagrant/source':
    ensure => link,
    mode => 0644,
    owner => 'vagrant',
    group => 'vagrant',
    target => '/vagrant',
  }

  notify {'download-and-install-splunk':
    message => "Don't forget to download & install Splunk from http://www.splunk.com. Also remember to install STOMP app (sudo ln -s /vagrant/stomp/ /opt/splunk/etc/apps/stomp) and restart Splunk (sudo /opt/splunk/bin/splunk restart)",
  }
}

include phase1
include phase2
