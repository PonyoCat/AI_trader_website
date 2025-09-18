import { APP_NAME } from "../config";

export default function Disclaimer() {
  
  // Simpel tekstside til juridisk information
  return (
    <div style={{ display: "grid", gap: 12 }}>
      <h3 style={{ marginTop: 0 }}>Disclaimer</h3>
      <p>
        Disclaimer
        <br></br>
The { APP_NAME } by Sinus Ho Service, including all apps, tools, models, and communications, is for educational and informational purposes only. 
It is not financial, investment, trading, legal, or tax advice, and it is not a solicitation to buy or sell any security or instrument. 
{ APP_NAME } is not your investment adviser, broker, dealer, or fiduciary.
<br></br>
<br></br>
AI generated outputs may be inaccurate, incomplete, or outdated. 
Information is provided “as is” and “as available,” without warranties of any kind, including accuracy, 
completeness, merchantability, fitness for a particular purpose, or non-infringement.
<br></br>
<br></br>
Trading involves substantial risk, including the risk of total loss. 
You are solely responsible for your decisions and for verifying any information before acting.
<br></br>
<br></br>
The Service may rely on third party data and may link to or interoperate with third party brokers and platforms. 
{ APP_NAME } does not control and is not responsible for third party content, services, outages, execution, fees, or losses. 
Any orders you place are between you and your broker.
<br></br>
<br></br>
To the maximum extent permitted by law, 
{ APP_NAME } and its owners, officers, employees, contractors, and affiliates are not liable for any damages
arising from your use of the Service. You agree to comply with all applicable laws and broker terms. 
{ APP_NAME } is not registered as an investment adviser or broker-dealer. 
These terms are governed by the laws of Denmark, with exclusive venue in Copenhagen City Court. 
By using the Service, you agree to this Disclaimer.
      </p>
    </div>
  );
}
