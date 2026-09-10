from locust import HttpUser, task, between

class FundUser(HttpUser):
    wait_time = between(0.05, 0.2)
    @task(3)
    def prices(self): self.client.get("/prices/RELIANCE.NS?limit=500")
    @task(1)
    def analytics(self): self.client.get("/analytics/RELIANCE.NS")
