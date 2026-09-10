using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Models
{
    public class DocumentQuery
    {
        public DateTime? startDate { get; set; }

        public DateTime? endDate { get; set; }

        public string queueName { get; set; }

    }
}
