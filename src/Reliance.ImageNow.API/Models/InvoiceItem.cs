using Reliance.ImageNow.API.Utitlities;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class InvoiceItem
    {
        [JsonConverter(typeof(EverythingToStringJsonConverter))]
        public string item_Description { get; set; }
        [JsonConverter(typeof(EverythingToStringJsonConverter))]
        public string Quantity { get; set; }
        [JsonConverter(typeof(EverythingToStringJsonConverter))]
        public string unit_price { get; set; }
        public string item_total { get; set; }
    }
}
