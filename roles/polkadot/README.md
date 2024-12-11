# Polkadot Validator Role

This role installs and configures a Polkadot validator node with security best practices and monitoring integration.

## Architecture

```mermaid
graph TD
    subgraph Validator Node
        A[Polkadot Service]
        B[Node Exporter]
        C[Grafana Agent]
        D[Promtail]
        M[Monit] --> |Monitor| C
        M --> |Monitor| B
        M --> |Monitor| D
    end

    subgraph External Services
        E[Prometheus]
        F[Loki]
        G[Grafana]
        E --> |Metrics| G
        F --> |Logs| G
    end
    
    subgraph Security
        H[Firewall]
        I[AppArmor]
        J[SSH]
        K[Binary Verify]
        L[Teleport Bastion]
    end

    A --> |Metrics| C
    B --> |Metrics| C
    D --> |Logs| C
    C --> |Metrics| E
    C --> |Logs| F

    H --> |Protect| A
    I --> |Secure| A
    J --> |Access| A
    K --> |Validate| A
    L --> |Access| A
```

## Role Tasks Sequence

```mermaid
sequenceDiagram
    participant Ansible
    participant System
    participant Service
    participant Binary

    Note over Ansible: Pre-tasks
    Ansible->>System: Verify OS requirements
    Ansible->>System: Create service user/group
    Ansible->>System: Setup directories

    Note over Ansible: Binary Management
    Ansible->>Binary: Download binary
    Ansible->>Binary: Verify signature
    Ansible->>Binary: Install to path
    
    Note over Ansible: Service Configuration
    Ansible->>System: Configure systemd unit
    Ansible->>System: Setup AppArmor profile
    Ansible->>System: Configure firewall rules
    
    Note over Ansible: Health Checks
    Ansible->>Service: Check binary version
    Ansible->>Service: Verify service status
    Ansible->>Service: Check sync status
    
    Note over Ansible: Monitoring Setup
    Ansible->>System: Configure metrics endpoint
    Ansible->>System: Setup log rotation
    Ansible->>System: Enable service monitoring
```

## Sync Process Sequence

```mermaid
sequenceDiagram
    participant Ansible
    participant System
    participant Service
    participant Snapshot
    participant Database

    Note over Ansible: Pre-Sync Preparation
    Ansible->>Service: Stop Polkadot service
    Ansible->>Database: Create backup of existing data
    Database-->>Ansible: Backup completed

    alt Snapshot Sync Enabled
        Note over Ansible: Snapshot Download
        Ansible->>Snapshot: Determine network snapshot
        Snapshot-->>Ansible: Provide snapshot URL
        Ansible->>System: Download snapshot
        System-->>Ansible: Download complete

        Note over Ansible: Snapshot Extraction
        Ansible->>System: Uncompress snapshot
        System->>Database: Extract to data directory
    end

    Note over Ansible: Sync Type Validation
    Ansible->>Ansible: Validate sync type
    alt Invalid Sync Type
        Ansible-->>Ansible: Fail with error
    else Valid Sync Type
        Note over Ansible: Sync Execution
        Ansible->>Service: Execute sync
        alt Sync Type: Warp
            Service->>Service: Perform warp sync
        else Sync Type: Fast
            Service->>Service: Perform fast sync
        else Sync Type: Full
            Service->>Service: Perform full sync
        end

        Note over Ansible: Sync Logging
        Ansible->>System: Log sync details
        System-->>Ansible: Log created
    end

    Note over Ansible: Post-Sync
    Ansible->>Service: Start Polkadot service
    Service-->>Ansible: Service started
```

## New Features

### Lifecycle Management
- Enhanced lifecycle management with sync, upgrade, and maintenance phases
- Comprehensive rollback mechanism for upgrades

### Backup Capabilities
- Automated backup and restore procedures
- Configurable retention policies and storage options

### Enhanced Health Monitoring
- Comprehensive health checks with configurable thresholds
- Process, port, and blockchain-specific monitoring
- Multi-level severity system (critical, high, low)
- Automated notifications via email and Slack

### Binary Management
- Support for multiple binary components (validator, execute-worker, prepare-worker)
- Version retention policy with configurable cleanup
- Binary verification with hash checking
- Pre and post-installation hooks

### Improved Backup System
- Automated backup procedures with compression
- Configurable retention policy
- Pattern-based exclusions
- Binary and database backup support

## Features

- Secure systemd service configuration
- Binary management with signature verification
- Firewall configuration
- Dedicated system user and group
- Directory structure management
- Prometheus metrics exposure
- AppArmor service protection
- Lifecycle management (sync, upgrade, maintenance)

## Requirements

- Ansible 2.9+
- Ubuntu 20.04+ / Debian 11+
- Python 3.8+
- Minimum 16GB RAM
- Minimum 500GB SSD storage

## Role Variables

### Binary Configuration
```yaml
polkadot_version: "stable2409-2"  # Using stable release format
polkadot_base_url: "https://github.com/paritytech/polkadot-sdk/releases/download"
binary_base_dir: "/usr/local/lib/polkadot"

polkadot_binaries:
  - name: "polkadot"
    link: "/usr/local/bin/polkadot"
  - name: "polkadot-execute-worker"
    link: "/usr/local/bin/polkadot-execute-worker"
  - name: "polkadot-prepare-worker"
    link: "/usr/local/bin/polkadot-prepare-worker"

# Version management
keep_previous_versions: 2
cleanup_old_versions: false
cleanup_wait_time: 300  # seconds
```

### Service Configuration
```yaml
polkadot_service_enabled: true
polkadot_service_state: "started"
polkadot_user: "polkadot"
polkadot_group: "polkadot"
```

### Directory Configuration
```yaml
polkadot_dirs:
  - "/data/polkadot"
  - "/var/run/polkadot"
  - "/var/log/polkadot"
  - "/home/polkadot/.local/share/polkadot"
```

### Node Configuration
```yaml
polkadot_node_name: "validator-1"
polkadot_chain: "polkadot"
polkadot_validator_mode: true
polkadot_telemetry_enabled: false
```

### Lifecycle Management
```yaml
lifecycle:
  sync:
    enabled: false    # Enable blockchain sync phase
  upgrade:
    enabled: false    # Enable binary upgrade phase
  maintenance:
    enabled: false    # Enable maintenance phase
  rollback:
    enabled: false    # Enable rollback mechanism for upgrades
```

### Backup Capabilities
```yaml
backup:
  enabled: true
  directory: "/var/backup/polkadot/binaries"
  retention_days: 7
  compress: true
  exclude_patterns:
    - "*.tmp"
    - "*.old"
```

### Health Check Configuration
```yaml
health_checks:
  enabled: true
  max_retries: 3
  retry_interval: 60
  timeout: 300  # 5 minutes

  # Process checks
  process_checks:
    - name: "Polkadot Validator Process"
      command: "pgrep -f 'polkadot.*--validator'"
      severity: critical

  # Port checks
  port_checks:
    - name: "P2P Port"
      port: 30333
      severity: critical
    - name: "RPC Port"
      port: 9933
      severity: high
    - name: "WebSocket Port"
      port: 9944
      severity: high
    - name: "Prometheus Port"
      port: 9615
      severity: low

  # Blockchain checks
  blockchain_checks:
    - name: "Block Production"
      min_blocks_per_hour: 240
      max_missed_blocks: 10
      severity: critical
    - name: "Peer Connectivity"
      min_peer_count: 3
      max_peer_count: 50
      severity: high
```

### Installation Hooks
```yaml
hooks:
  pre_install:
    - name: "backup_db"
      enabled: true
      command: "/usr/local/bin/backup_polkadot_db.sh"
      timeout: 3600
    - name: "stop_service"
      enabled: true
      command: "systemctl stop polkadot"
      timeout: 300
  post_install:
    - name: "start_service"
      enabled: true
      command: "systemctl start polkadot"
      timeout: 300
```

### AppArmor Configuration
```yaml
apparmor:
  enabled: true
  profiles:
    polkadot:
      enabled: true    # Enable AppArmor profile for Polkadot
      enforce: true    # Set to enforce mode (false for complain mode)
```

## Dependencies

Required Ansible collections:
- community.general
- ansible.posix

## Example Playbook

```yaml
- hosts: validators
  roles:
    - role: polkadot
      vars:
        polkadot_node_name: "validator-1"
        polkadot_validator_mode: true
        polkadot_telemetry_enabled: false
```

## Usage

### Basic Installation
```bash
# Run basic installation and setup
ansible-playbook playbook.yaml
```

### Lifecycle Operations

The role supports different lifecycle operations that can be triggered via command-line parameters:

1. **Sync Operation**
   ```bash
   # Trigger blockchain sync
   ansible-playbook playbook.yaml -e "lifecycle.sync.enabled=true"
   ```

2. **Upgrade Operation**
   ```bash
   # Perform binary upgrade
   ansible-playbook playbook.yaml -e "lifecycle.upgrade.enabled=true"
   ```

3. **Maintenance Operation**
   ```bash
   # Run maintenance tasks
   ansible-playbook playbook.yaml -e "lifecycle.maintenance.enabled=true"
   ```

4. **Rollback Operation**
   ```bash
   # Trigger rollback mechanism for upgrades
   ansible-playbook playbook.yaml -e "lifecycle.rollback.enabled=true"
   ```

Note: Lifecycle operations are mutually exclusive. When a lifecycle operation is active, the basic setup tasks will not run.

## Security Features

- Dedicated system user with minimal privileges
- Systemd service hardening:
  * PrivateTmp=true
  * NoNewPrivileges=true
  * ProtectSystem=strict
  * ProtectHome=true
  * ReadWritePaths restrictions
- Firewall with restrictive rules
- Binary signature verification
- AppArmor Mandatory Access Control:
  * Fine-grained resource access control
  * Network access restrictions
  * File system access limitations
  * Protection against privilege escalation

## Directory Structure

```
/data/polkadot/
├── config.json         # Node configuration
└── chain-data/         # Blockchain data

/var/run/polkadot/
└── polkadot.pid       # Process ID file

/var/log/polkadot/
└── polkadot.log       # Service logs

/home/polkadot/.local/share/polkadot/
├── chains/            # Chain-specific data
└── keystore/          # Node keys
```

## Service Management

The role configures a systemd service with:
- Automatic restart on failure
- Resource limits
- Security restrictions
- Proper logging

## Monitoring Integration

### Prometheus Metrics
- Exposed on port 9615
- Node-specific metrics
- Validator performance metrics
- System resource usage

## Testing

This role includes Molecule tests:

```bash
# Install test dependencies
pip install molecule molecule-docker ansible-lint

# Run tests
cd roles/polkadot
molecule test
```

The tests verify:
- Binary installation
- Service configuration
- Directory permissions
- Port availability
- User/group creation
- Monitoring integration

## License

Apache-2.0

## Author Information

Created by [Your Name]
