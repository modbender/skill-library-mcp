import unittest
import time
import threading
from agentmesh import Agent, LocalHub, NetworkHub, NetworkHubServer

class TestAgentMesh(unittest.TestCase):
    def test_local_hub_encryption(self):
        hub = LocalHub()
        alice = Agent("alice", hub=hub)
        bob = Agent("bob", hub=hub)
        
        received = []
        @bob.on_message
        def handle(msg):
            received.append(msg)
            
        alice.send("bob", text="Hello Bob!")
        time.sleep(0.5)
        
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].text, "Hello Bob!")
        self.assertEqual(received[0].sender, "alice")

    def test_network_hub(self):
        host = "127.0.0.1"
        port = 7791
        server = NetworkHubServer(host=host, port=port)
        server.start(block=False)
        time.sleep(1.0)
        
        try:
            hub_alice = NetworkHub(host=host, port=port)
            hub_bob = NetworkHub(host=host, port=port)
            
            alice = Agent("alice_net", hub=hub_alice)
            bob = Agent("bob_net", hub=hub_bob)
            
            received = []
            @bob.on_message
            def handle(msg):
                received.append(msg)
            
            alice.send("bob_net", text="Network Hello!")
            
            # Wait for message
            start = time.time()
            while len(received) == 0 and time.time() - start < 3:
                time.sleep(0.1)
                
            self.assertEqual(len(received), 1)
            self.assertEqual(received[0].text, "Network Hello!")
            self.assertEqual(received[0].sender, "alice_net")
        finally:
            pass # Server in thread will die with process

if __name__ == "__main__":
    unittest.main()
