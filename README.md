<div align='center'>
  
# ***Lab 2 Reliable Transport over UDP***   
**Michael Newman**  
**Networking & Telecomm. - CPAN - 226 - RNA**  
**Professor Sergio Coelho Loza**  
**February 6, 2026**  

</div>
<br>
<br>
<br>
<br>

### Buffer Logic
#### **Server.py:**
The buffer in server.py works like a deli lineup for data packets. Each packet gets a sequence number. When a packet arrives before its turn it gets placed in the buffer and the process continues, then when it’s expected in the sequence the waiting packet is popped into its position, and the loop continues until all of the packets are in the correct order.

#### **Client.py:**
The buffer in client.py is for retransmitting the packets. The way it works is that every packet gets timestamped and receives an ack status. If the packet doesn’t have an ack then it resends the packet and restarts the timer.
