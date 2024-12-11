# Admin Role: System Hardening and Configuration

This role manages system administration tasks, monitoring, and secure access for validator nodes, with a focus on hardening and configuration.

## New Features

### Resource Monitoring
- Comprehensive resource monitoring with configurable thresholds
- Alerts via Slack and email
- Integration with Grafana Agent for detailed metrics
- Prometheus and Alertmanager for monitoring and alerting
- Protected access to monitoring endpoints via Teleport
- SmartCTL monitoring for disk health and SMART metrics

## Features

- UFW firewall configuration
- Grafana Agent for metrics collection
- Prometheus monitoring and alerting
- Node Exporter for system metrics
- Teleport for secure SSH and application access
- Binary signature verification

### 🔐 Protected Services via Teleport
- **Monitoring Endpoints**
  - Prometheus UI (`prometheus.<nodename>`)
  - Alertmanager UI (`alertmanager.<nodename>`)
  - Node Exporter Metrics (`node-exporter.<nodename>`)
  - SmartCTL Metrics (`smartctl.<nodename>`)
- **Validator Endpoints**
  - Polkadot Metrics (`metrics-polkadot.<nodename>`)
  - Polkadot RPC (`rpc-polkadot.<nodename>`)

### 🔒 Security Hardening
#### AppArmor Service Protection
- Mandatory Access Control (MAC) for all services
- Fine-grained resource access control
- Enforced security profiles for each service
- Protection against privilege escalation
- Network access control per service
- File system access restrictions

#### Shared Memory Protection
- Secure mounting of `/dev/shm`
- Prevents code execution in shared memory
- Configurable security options

#### SSH Protection with Fail2ban
- Brute-force attack mitigation
- Customizable ban times and retry limits
- Multi-service SSH protection

### 🛡️ Configuration Options

#### Prometheus Rules
```yaml
# Example monitoring rules structure
groups:
  - name: heartbeat_rules
    rules:
      - alert: InstanceDown
        expr: up == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Instance {{ '$labels.instance' }} down"

  - name: disk_health
    rules:
      - alert: SmartctlDeviceError
        expr: smartctl_device_smart_healthy == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "SMART health check failed on {{ '$labels.device' }}"

  - name: node_monitoring
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ '$labels.instance' }}"
```

#### Teleport Application Service
```yaml
teleport:
  enabled: true
  app_service:
    enabled: true
    apps:
      monitoring:
        - name: prometheus
          uri: "http://localhost:9090"
        - name: alertmanager
          uri: "http://localhost:9093"
        - name: node-exporter
          uri: "http://localhost:9100"
        - name: smartctl
          uri: "http://localhost:9633"
      validators:
        - name: polkadot
          ports:
            metrics: 9615
            rpc: 9944
```

#### Shared Memory Hardening
```yaml
hardening:
  shared_memory:
    enabled: true  # Enable/disable
    mount_options: 
      - noexec     # Prevent code execution
      - nosuid     # Prevent setuid binaries
      - nodev      # Prevent device files
```

#### Fail2ban Configuration
```yaml
hardening:
  fail2ban:
    enabled: true  # Enable/disable Fail2ban
    ssh:
      max_retry: 5     # Allowed login attempts
      ban_time: 7200   # Ban duration (seconds)
      find_time: 1200  # Time window for retry attempts
    services:
      - name: sshd
        enabled: true
      - name: ssh
        enabled: false
```

#### AppArmor Configuration
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
    teleport:
      enabled: true
      enforce: true
    smartctl_exporter:
      enabled: true
      enforce: true
```

#### Grafana Agent Configuration
```yaml
grafana_agent:
  version: "0.39.1"
  enabled: true
  remote_write:
    - url: "http://prometheus:9090/api/v1/write"
  integrations:
    node_exporter:
      enabled: true
    smartctl:
      enabled: true
```

#### SmartCTL Exporter Configuration
```yaml
smartctl_exporter:
  enabled: true
  version: "0.11.0"
  port: 9633
  devices:
    - /dev/sda
    - /dev/sdb
```

## Requirements

- Ansible 2.9+
- Ubuntu 20.04+ / Debian 11+
- Python 3.8+

## Role Variables

### UFW Configuration
```yaml
ufw:
  enabled: true
  default_incoming_policy: "deny"
  default_outgoing_policy: "allow"
  rules:
    - { port: 22, proto: "tcp", rule: "allow" }
    - { port: 3022, proto: "tcp", rule: "allow" }
```

### Node Exporter Configuration
```yaml
node_exporter:
  version: "1.7.0"
  enabled: true
  port: 9100
```

### Teleport Configuration
```yaml
teleport:
  enabled: true
  version: "13.3.2"
  auth_token: ""  # Required
  auth_server: "" # Required
```

### Hardening Configuration
```yaml
hardening:
  shared_memory:
    enabled: true  # Enable/disable
    mount_options: 
      - noexec     # Prevent code execution
      - nosuid     # Prevent setuid binaries
      - nodev      # Prevent device files
  fail2ban:
    enabled: true  # Enable/disable Fail2ban
    ssh:
      max_retry: 5     # Allowed login attempts
      ban_time: 7200   # Ban duration (seconds)
      find_time: 1200  # Time window for retry attempts
    services:
      - name: sshd
        enabled: true
      - name: ssh
        enabled: false
```

## Architecture

```mermaid
graph TD
    subgraph Monitoring Node
        A[Node Exporter]
        B[Grafana Agent]
        C[Promtail]
        M[Teleport] --> |Monitor| B
        M --> |Monitor| A
        M --> |Monitor| C
    end

    subgraph External Services
        D[Prometheus]
        E[Loki]
        F[Grafana]
        D --> |Metrics| F
        E --> |Logs| F
    end
    
    subgraph Security Layer
        G[Firewall]
        H[AppArmor]
        I[SSH]
        J[Teleport Bastion]
    end

    A --> |Metrics| B
    C --> |Logs| B
    B --> |Metrics| D
    B --> |Logs| E

    G --> |Protect| B
    H --> |Secure| B
    I --> |Access| B
    J --> |Access| B
```

## Services Interaction

```mermaid
graph LR
    subgraph Local Services
        A[Grafana Agent]
        B[Node Exporter]
        C[Promtail]
        T[Teleport]
        
        subgraph Security Layer
            E[Firewall]
            F[AppArmor]
            G[SSH]
        end
    end

    subgraph Remote Services
        H[Prometheus]
        I[Grafana]
        J[Loki]
        K[Teleport Bastion]
    end

    B --> |Metrics| A
    C --> |Logs| A
    A --> |Metrics| H
    A --> |Logs| J
    H --> |Metrics| I
    T --> |Access| K

    E --> |Protect| A
    F --> |MAC| A
    F --> |MAC| B
    F --> |MAC| C
    F --> |MAC| T
    G --> |Access| A
```

## Dependencies

Required Ansible collections:
- community.general
- ansible.posix

## Example Playbook

```yaml
- hosts: validators
  roles:
    - role: admin
      vars:
        teleport:
          auth_token: "your-auth-token"
          auth_server: "auth.example.com:3025"
        promtail:
          enabled: true
          loki_url: "http://loki.example.com:3100"
        hardening:
          shared_memory:
            enabled: true
          fail2ban:
            enabled: true
            ssh:
              max_retry: 5
        apparmor:
          enabled: true
          profiles:
            grafana_agent:
              enabled: true
              enforce: true
            node_exporter:
              enabled: true
              enforce: true
            teleport:
              enabled: true
              enforce: true
            smartctl_exporter:
              enabled: true
              enforce: true
```

## Security Features

- Binary signature verification for all downloaded binaries
- UFW firewall with restrictive default policies
- Secure service configurations with minimal privileges
- Dedicated system users for each service
- Systemd service hardening
- Shared memory protection
- SSH protection with Fail2ban
- AppArmor service protection

## Monitoring Stack

### Grafana Agent
- Metrics collection
- Remote write to Prometheus
- Service discovery

### Node Exporter
- System metrics collection
- Hardware monitoring
- Resource utilization tracking

## Testing

This role includes Molecule tests for verifying functionality:

```bash
# Install test dependencies
pip install molecule molecule-docker ansible-lint

# Run tests
cd roles/admin
molecule test
```

The tests verify:
- Package installation
- Service configuration
- Port availability
- Binary installation
- Configuration files
- System users
- UFW rules

## License

Apache-2.0

## Author Information

Created by [Your Name]
