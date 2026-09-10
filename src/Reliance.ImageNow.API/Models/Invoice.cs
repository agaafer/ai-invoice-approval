using Reliance.ImageNow.API.Utitlities;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class Invoice
    {
        public string vendor { get; set; }
        public string invoice_number { get; set; }
        public string invoice_date { get; set; }
        public string invoice_due_date { get; set; }
        public string ship_to_address { get; set; }
        public string vendor_address { get; set; }
        public List<InvoiceItem> invoice_items { get; set; }
        public string items_subtotal { get; set; }
        public string invoice_tx { get; set; }
        [JsonConverter(typeof(EverythingToStringJsonConverter))]
        public string invoice_total { get; set; }
      
        public string purchase_order_number { get; set; }        

    }
}
