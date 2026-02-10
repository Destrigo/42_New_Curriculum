*This project has been created as part of the 42 curriculum by mtaranti.*

# NetPractice

## Description

NetPractice is a hands-on networking exercise designed to introduce fundamental computer networking concepts through practical configuration challenges. The project consists of 10 progressively difficult levels where you must configure network diagrams to establish proper communication between devices.

### Project Goals

- Master TCP/IP addressing and subnetting
- Understand routing concepts and gateway configuration
- Learn to troubleshoot network connectivity issues
- Gain practical experience with network topology design

### What You'll Learn

Through completing this project, you will develop a solid understanding of:
- How IP addresses work and how to assign them correctly
- The role of subnet masks in network segmentation
- Default gateway configuration for inter-network communication
- Routing tables and packet forwarding
- Network troubleshooting using systematic analysis

## Instructions

### Setup

1. **Extract the Project Files**
   ```bash
   tar -xzf net_practice.tgz
   cd net_practice
   ```

2. **Launch the Interface**
   - Open `index.html` in **Google Chrome** or a **Chromium-based browser**
   - ⚠️ **Important**: Firefox is not compatible with this training interface

3. **Enter Your Login**
   - On the welcome screen, enter your 42 intranet login
   - This ensures your configurations are personalized
   - Select "Training" mode to access the 10 levels

### Completing the Levels

Each level presents a non-functioning network diagram with specific goals:

1. **Analyze the Network**
   - Identify devices (hosts, routers, switches)
   - Note which fields are editable (unshaded)
   - Read the objectives at the top of the screen

2. **Configure the Network**
   - Fill in IP addresses, subnet masks, and gateways
   - Ensure devices on the same link share a subnet
   - Configure routing tables on routers

3. **Verify Your Configuration**
   - Click **"Check again"** to test your setup
   - Read the logs at the bottom for error messages
   - Adjust configuration based on feedback

4. **Export Your Solution**
   - Once successful, click **"Get my config"**
   - Save the JSON file as `levelX.json`
   - ⚠️ **Critical**: Do this for EVERY level before proceeding

### Submission Requirements

Your Git repository must contain:

```
netpractice/
├── README.md          (this file)
├── level1.json        (exported configuration)
├── level2.json
├── level3.json
├── level4.json
├── level5.json
├── level6.json
├── level7.json
├── level8.json
├── level9.json
└── level10.json
```

**Important Notes:**
- Place all 10 JSON files in the repository root
- Each file must be properly exported from the interface
- Do not manually edit the JSON files

### Evaluation Process

During your defense, you will:

1. Present your completed configurations
2. Complete **3 random levels** within a time limit
3. Explain your networking decisions
4. Demonstrate understanding of the concepts

**Allowed Tools:**
- Basic calculator (e.g., `bc`) for subnet calculations
- ⚠️ No external subnet calculators or network tools

## Resources

### Core Networking Concepts Studied

#### 1. TCP/IP Addressing
- **IPv4 Structure**: 32-bit addresses written as four octets (e.g., 192.168.1.10)
- **Network vs Host Portions**: Division determined by subnet mask
- **Private IP Ranges**: 
  - Class A: 10.0.0.0/8
  - Class B: 172.16.0.0/12
  - Class C: 192.168.0.0/16

#### 2. Subnet Mask
- **Purpose**: Defines network and host portions of an IP address
- **Common Masks**:
  - /24 (255.255.255.0): 254 usable hosts
  - /25 (255.255.255.128): 126 usable hosts
  - /26 (255.255.255.192): 62 usable hosts
  - /27 (255.255.255.224): 30 usable hosts
  - /28 (255.255.255.240): 14 usable hosts
  - /30 (255.255.255.252): 2 usable hosts (point-to-point)
- **CIDR Notation**: Slash notation indicating network bits (e.g., /24)

#### 3. Default Gateway
- **Definition**: Router interface that forwards packets to other networks
- **Configuration**: Must be in the same subnet as the host
- **Purpose**: Enables communication beyond the local network

#### 4. Routers and Switches
- **Router**: 
  - Operates at Layer 3 (Network)
  - Connects different networks
  - Makes forwarding decisions based on IP addresses
  - Maintains routing tables
- **Switch**: 
  - Operates at Layer 2 (Data Link)
  - Connects devices within the same network
  - Forwards based on MAC addresses

#### 5. Routing Tables
- **Components**:
  - Destination network
  - Subnet mask
  - Next hop (gateway or interface)
- **Default Route**: 0.0.0.0/0 catches all non-specific traffic

#### 6. OSI Model Layers (Relevant to This Project)
- **Layer 3 (Network)**: IP addressing, routing
- **Layer 2 (Data Link)**: Switching, MAC addresses
- **Layer 1 (Physical)**: Cable connections

### Learning Resources

#### Official Documentation
- [RFC 791 - Internet Protocol](https://tools.ietf.org/html/rfc791)
- [RFC 1918 - Private Address Space](https://tools.ietf.org/html/rfc1918)
- [RFC 950 - Internet Standard Subnetting Procedure](https://tools.ietf.org/html/rfc950)

#### Tutorials and Guides
- [Cisco Networking Basics](https://www.cisco.com/c/en/us/solutions/small-business/resource-center/networking/networking-basics.html)
- [Subnetting Made Easy](https://www.practicalnetworking.net/stand-alone/subnetting-mastery/)
- [Understanding IP Addressing](https://www.cloudflare.com/learning/network-layer/what-is-an-ip-address/)
- [TCP/IP Guide](http://www.tcpipguide.com/)

#### Tools for Practice
- Binary/Decimal conversion tools
- Subnet calculators (for study, not during evaluation)
- Network diagram software for planning

### Use of AI in This Project

AI assistance was utilized for the following purposes:

#### Learning and Understanding
- Clarifying complex networking concepts (subnetting, CIDR notation)
- Generating examples of network configurations
- Explaining routing table entries
- Verifying subnet calculations

#### Documentation
- Structuring this README
- Creating comprehensive study materials
- Organizing concept explanations

#### NOT Used For
- ❌ Solving the actual level configurations
- ❌ Generating the JSON export files
- ❌ Completing the required exercises

**Philosophy**: AI served as a study companion and concept explainer, similar to consulting textbooks or tutorials. All actual problem-solving and configuration work was completed independently to ensure genuine understanding required for the evaluation.

## Technical Notes

### Subnet Calculation Quick Reference

```
CIDR    Subnet Mask       Wildcard Mask    Usable Hosts    Network Size
/30     255.255.255.252   0.0.0.3          2               4
/29     255.255.255.248   0.0.0.7          6               8
/28     255.255.255.240   0.0.0.15         14              16
/27     255.255.255.224   0.0.0.31         30              32
/26     255.255.255.192   0.0.0.63         62              64
/25     255.255.255.128   0.0.0.127        126             128
/24     255.255.255.0     0.0.0.255        254             256
```

### Common IP Address Special Cases

- **Network Address**: First IP in subnet (e.g., 192.168.1.0/24)
  - Cannot be assigned to hosts
  - Identifies the network itself

- **Broadcast Address**: Last IP in subnet (e.g., 192.168.1.255/24)
  - Cannot be assigned to hosts
  - Used to send packets to all devices in subnet

- **Loopback**: 127.0.0.0/8
  - Used for localhost communication
  - Most commonly 127.0.0.1

- **Link-Local**: 169.254.0.0/16
  - Auto-assigned when DHCP fails (APIPA)
  - Only for local network communication

### Troubleshooting Checklist

When a configuration doesn't work, check:

1. ✅ Are all IPs in the same link using the same subnet?
2. ✅ Is the subnet mask consistent across connected devices?
3. ✅ Does the gateway IP exist on the router's interface?
4. ✅ Is the gateway in the same subnet as the host?
5. ✅ Are routing table entries pointing to correct next hops?
6. ✅ Are you avoiding network IDs and broadcast addresses?
7. ✅ Are there any IP address conflicts?
8. ✅ Do all paths have a route (no dead ends)?

## Key Takeaways

### What I Learned

1. **IP Addressing Fundamentals**
   - How to calculate network IDs and broadcast addresses
   - The relationship between subnet masks and usable IP ranges
   - Proper IP address assignment within constraints

2. **Subnetting Skills**
   - Converting between CIDR notation and dotted decimal
   - Dividing networks into appropriately-sized subnets
   - Calculating the number of available hosts

3. **Routing Concepts**
   - How routing tables direct traffic
   - The role of default routes (0.0.0.0/0)
   - Multi-hop routing through intermediate routers

4. **Network Design**
   - Efficient IP address space utilization
   - Logical network segmentation
   - Scalable addressing schemes

### Challenges Encountered

[Add your specific challenges here during the project]

Examples:
- Understanding how /30 subnets work for point-to-point links
- Properly configuring routing tables with multiple routes
- Calculating subnet boundaries for non-standard masks

### Skills Developed

- **Technical Skills**:
  - Binary and decimal conversion
  - Subnet mask calculation
  - Network troubleshooting methodology
  - Reading network diagrams

- **Problem-Solving Skills**:
  - Systematic debugging approach
  - Understanding error messages
  - Testing and verification
  - Attention to detail

## Exam Preparation

### Mental Math for Subnets

Practice these conversions:
- Powers of 2: 2, 4, 8, 16, 32, 64, 128, 256
- Common subnet sizes: /24, /25, /26, /27, /28, /30
- Quickly identify network boundaries

### Using `bc` Calculator

```bash
# Convert decimal to binary
echo "obase=2; 192" | bc
# Output: 11000000

# Calculate power of 2
echo "2^5" | bc
# Output: 32

# Calculate number of hosts
echo "2^8 - 2" | bc
# Output: 254 (for /24)
```

### Time Management

During evaluation (3 random levels):
- **Level 1-3**: ~2-3 minutes each (simple)
- **Level 4-7**: ~5-7 minutes each (intermediate)
- **Level 8-10**: ~10-15 minutes each (complex)

Practice until you can complete any level quickly and explain your reasoning.

## Project Structure

```
This is a web-based training interface:
- HTML/CSS/JavaScript frontend
- Client-side network simulation
- JSON export for configuration saving
- No backend server required
```

## Author

**[YOUR_LOGIN]** - 42 Network Student

---

*For questions or issues with this project, consult your peers, the 42 network documentation, or your evaluation team.*
