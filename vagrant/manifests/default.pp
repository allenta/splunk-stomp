Exec {
  path => ['/bin/', '/sbin/' , '/usr/bin/', '/usr/sbin/']
}

class system-update {
  exec {'apt-get-update':
    command => '/usr/bin/apt-get update'
  }

  package {['python', 'python-pip']:
    ensure => present,
    require => Exec['apt-get-update'],
  }
}

class rabbitmq {
  Class['system-update'] -> Class['rabbitmq']

  exec {'add-rabbitmq-source':
    user => 'root',
    creates => "/home/vagrant/.vagrant.add-rabbitmq-source",
    command => "echo \"deb http://www.rabbitmq.com/debian/ testing main\" >> /etc/apt/sources.list && wget http://www.rabbitmq.com/rabbitmq-signing-key-public.asc -O /tmp/rabbitmq-signing-key-public.asc && apt-key add /tmp/rabbitmq-signing-key-public.asc && touch /home/vagrant/.vagrant.add-rabbitmq-source",
  }

  exec {'apt-get-update-rabbitmq':
    command => '/usr/bin/apt-get update',
    require => Exec['add-rabbitmq-source'],
  }

  package {['rabbitmq-server']:
    ensure => present,
    require => Exec['apt-get-update-rabbitmq'],
  }

  exec {'enable-rabbitmq-stomp-and-management':
    user => 'root',
    creates => "/home/vagrant/.vagrant.enable-rabbitmq-stomp-and-management",
    command => "rabbitmq-plugins enable rabbitmq_management && rabbitmq-plugins enable rabbitmq_stomp && touch /home/vagrant/.vagrant.enable-rabbitmq-stomp-and-management",
    require => Package['rabbitmq-server'],
  }
}

class user {
  Class['system-update'] -> Class['user']

  package {['virtualenv']:
    ensure   => 'installed',
    provider => 'pip',
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

include system-update
include rabbitmq
include user
