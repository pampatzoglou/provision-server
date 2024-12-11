# provision-server

```
## Overview

This Ansible collection provides a comprehensive, secure, and automated solution for deploying and managing servers with a focus on Polkadot validator nodes. Designed with a focus on security, observability, and reliability, the collection offers robust infrastructure-as-code capabilities.


## Architecture

```mermaid
graph LR
    subgraph Access
        H[Firewall]
        I[SSH Hardening]
        K[AppArmor MAC]
        J[Teleport (agent)]
    end

    subgraph External Services
        P[Prometheus]
        L[Loki]
        A[Alertmanager]
        TB[Teleport Bastion]
        G --> |Metrics| P
        G --> |Metrics| PL
        G --> |Logs| L
    end

    subgraph Monitoring
        N[Node Exporter]
        S[smartctl Exporter]
        G[Grafana Agent]
        PL[Prometheus (local)]
        AL[Alertmanager(local)]

        N --> |Monitor| G
        S --> |Monitor| G
        G --> |Metrics| PL
        PG --> |Metrics| AL
        G --> |Logs| P
        G --> |Logs| L    
    end

```

## Security and Hardening Features

### System Hardening

- **Shared Memory Protection**

  - Secure mounting of `/dev/shm`
  - Prevents code execution, setuid, and device access
  - Configurable mount options
- **Fail2ban SSH Protection**

  - Configurable brute-force attack mitigation
  - Customizable ban times and retry attempts
  - Multi-service support (SSH)
- **AppArmor Service Protection**

  - Mandatory Access Control (MAC) for all services
  - Fine-grained resource access control
  - Enforced security profiles
  - Protection against privilege escalation
  - Network and file system access restrictions

### Monitoring and Alerting

- Comprehensive system monitoring
- Centralized log management
- Proactive alerting
- **OpsGenie Heartbeats**
  - Configurable service health monitoring
  - Multiple heartbeat endpoints
  - Flexible interval settings

## Dynamic Inventory Configuration

This project supports dynamic inventory for both AWS and DigitalOcean cloud providers.

### Prerequisites

1. Install required collections:

```bash
ansible-galaxy collection install -r requirements.yml
```

2. Configure cloud provider credentials:

For AWS, set the following environment variables:

```bash
export AWS_ACCESS_KEY_ID='your_aws_access_key'
export AWS_SECRET_ACCESS_KEY='your_aws_secret_key'
```

For DigitalOcean, set the API token:

```bash
export DO_API_TOKEN='your_digitalocean_api_token'
```

### Usage

To list all hosts from a specific provider:

```bash
# List AWS hosts
ansible-inventory -i inventory/aws_ec2.yml --list

# List DigitalOcean hosts
ansible-inventory -i inventory/digitalocean.yml --list
```

To use both providers in a playbook:

```bash
ansible-playbook -i inventory/aws_ec2.yml -i inventory/digitalocean.yml playbook.yaml
```

## Bare Metal Inventory

The project supports multiple ways to manage bare metal hosts:

1. **Static YAML Inventory**

   - Define hosts in YAML files under `inventory/hosts/`
   - Supports grouping and custom variables
   - Example provided in `inventory/hosts/bare_metal_example.yml`
2. **Netbox Integration**

   - Automatically discover hosts from Netbox DCIM
   - Groups hosts by device roles, sites, and racks
   - Configure with environment variables:

   ```bash
   export NETBOX_URL='https://netbox.example.com'
   export NETBOX_TOKEN='your_netbox_api_token'
   ```
3. **Proxmox Integration**

   - Discover hosts from Proxmox clusters
   - Includes both VMs and containers
   - Configure with environment variables:

   ```bash
   export PROXMOX_URL='https://proxmox.example.com:8006'
   export PROXMOX_USER='root@pam'
   export PROXMOX_PASSWORD='your_proxmox_password'
   ```

To use bare metal inventory:

```bash
# List all bare metal hosts
ansible-inventory -i inventory/bare_metal.yml --list

# Use with specific groups
ansible-playbook -i inventory/bare_metal.yml playbook.yaml --limit validators

# Combine with cloud providers
ansible-playbook -i inventory/aws_ec2.yml -i inventory/digitalocean.yml -i inventory/bare_metal.yml playbook.yaml
```

## Quick Configuration Examples

### Hardening Configuration

```yaml
hardening:
  shared_memory:
    enabled: true
    mount_options: 
      - noexec
      - nosuid
      - nodev
  
  fail2ban:
    enabled: true
    ssh:
      max_retry: 5
      ban_time: 7200  # 2 hours
      find_time: 1200  # 20 minutes
    services:
      - name: sshd
        enabled: true
```

### AppArmor Configuration

```yaml
apparmor:
  enabled: true  # Master switch for AppArmor
  profiles:
    grafana_agent:
      enabled: true   # Enable profile for Grafana Agent
      enforce: true   # Enforce mode (false for complain mode)
    node_exporter:
      enabled: true
      enforce: true
    promtail:
      enabled: true
      enforce: true
    monit:
      enabled: true
      enforce: true
    teleport:
      enabled: true
      enforce: true
```

## Roles

### Admin Role

- System-level configurations
- Security hardening
- Monitoring stack setup
- User and group management

### Access Role
- **Author**: Pantelis Ampatzoglou  
- **Description**: Comprehensive system administration role for Polkadot validator nodes, including security hardening, monitoring, and alerting capabilities.  
- **License**: Apache-2.0  
- **Minimum Ansible Version**: 2.9  

### Monitoring Role
- **Author**: Pantelis Ampatzoglou  
- **Description**: Comprehensive system administration role for Polkadot validator nodes, including security hardening, monitoring, and alerting capabilities.  
- **License**: Apache-2.0  
- **Minimum Ansible Version**: 2.9  

### Polkadot Role

- Validator node deployment
- Binary management
- Service configuration
- Monitoring integration

## Prerequisites

- Ansible 2.9+
- Ubuntu 20.04/22.04 LTS
- Python 3.8+
- pip3
- virtualenv
- git

## Installation

### Setup virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install molecule molecule-docker ansible ansible-lint
```

1. Install Ansible collections:

```bash
source venv/bin/activate
ansible-galaxy install -r requirements.yml
```

2. Configure your inventory and variables

## Configuration

Customize deployment through role variables in `group_vars` or `host_vars`:

- `polkadot_version`: Specify Polkadot binary version
- `validator_name`: Set your validator's name
- `monitoring_enabled`: Enable/disable monitoring components

## Testing

Uses Molecule for automated testing:

- Docker-based test environments
- Comprehensive role verification
- Scenario-based testing

## Security Considerations

- Regular updates to binary signatures
- Periodic security audits
- Minimal exposed ports
- Strict authentication mechanisms

## Usage

```bash
source venv/bin/activate
ansible-playbook --ask-become-pass -e user=$USER playbook.yaml
```

### Lifecycle Operations

The playbook supports different lifecycle operations for managing Polkadot validator nodes:

1. **Initial Setup**

   ```bash
   ansible-playbook playbook.yaml
   ```
2. **Blockchain Sync**

   ```bash
   ansible-playbook playbook.yaml -e "lifecycle.sync.enabled=true"
   ```
3. **Binary Upgrade**

   ```bash
   ansible-playbook playbook.yaml -e "lifecycle.upgrade.enabled=true"
   ```
4. **Maintenance**

   ```bash
   ansible-playbook playbook.yaml -e "lifecycle.maintenance.enabled=true"
   ```
5. **Health Checks**

   ```bash
   ansible-playbook playbook.yaml --tags health
   ```

Note: Lifecycle operations are mutually exclusive. When a lifecycle operation is active, the basic setup tasks will not run.

### Tags

The playbook supports various tags for targeted execution:

- `setup`: Run only setup tasks
- `lifecycle`: Run lifecycle management tasks
- `sync`: Run blockchain sync tasks
- `upgrade`: Run upgrade tasks
- `maintenance`: Run maintenance tasks
- `security`: Run security-related tasks
- `monitoring`: Run monitoring-related tasks
- `apparmor`: Run AppArmor configuration tasks

Example:

```bash
# Run only security-related tasks
ansible-playbook playbook.yaml --tags security

# Run setup and monitoring tasks
ansible-playbook playbook.yaml --tags "setup,monitoring"
```

## Contributing

1. Clone the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a Pull Request

## License

Apache-2.0 License - See [LICENSE](LICENSE) file for details.

## Documentation

For detailed documentation on each role, please refer to:

- [Access Role Documentation](roles/access/README.md)
- [Monitoring Role Documentation](roles/monitoring/README.md)
- [Polkadot Role Documentation](roles/polkadot/README.md)

## Contact

Maintained by the Polkadot Validator Infrastructure Team
