using Microsoft.EntityFrameworkCore;
using Reliance.ImageNow.API.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Data
{
    public class AppDbContext : DbContext
    {
        public DbSet<Document> Documents { get; set; }
        public DbSet<WorkflowQueue> WorkflowQueues { get; set; }

        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        protected override void OnModelCreating(ModelBuilder builder)
        {
            base.OnModelCreating(builder);
            builder.HasDefaultSchema("inuser");
      
            builder.Entity<Document>(
                doc =>
                {
                    
                    doc.ToTable("IN_DOC");
                    doc.Property(o => o.Id).HasColumnName("DOC_ID");
                    doc.Property(o => o.InstanceId).HasColumnName("INSTANCE_ID");
                    doc.Property(o => o.VendorID).HasColumnName("FOLDER");
                    doc.Property(o => o.VendorName).HasColumnName("TAB");
                    doc.Property(o => o.InvoiceNumber).HasColumnName("F3");
                    doc.Property(o => o.DocumentTypeId).HasColumnName("DOC_TYPE_ID");
                   

                }
                );

            builder.Entity<Instance>(
                ins =>
                {

                    ins.ToTable("IN_INSTANCE");
                    ins.Property(o => o.Id).HasColumnName("INSTANCE_ID");
                    ins.Property(o => o.CreatedDateTime).HasColumnName("CREATION_TIME");
                    ins.Property(o => o.ModifiedDateTime).HasColumnName("MOD_TIME");

                }
                );
            builder.Entity<WorkflowItem>(
               itm =>
               {

                   itm.ToTable("IN_WF_ITEM");
                   itm.Property(o => o.Id).HasColumnName("ITEM_ID");
                   itm.Property(o => o.WorkflowQueueId).HasColumnName("QUEUE_ID");
                   itm.Property(o => o.InstanceId).HasColumnName("INSTANCE_ID");
                   itm.Property(o => o.WorkflowStartTime).HasColumnName("QUEUE_START_TIME");

               }
               );
            builder.Entity<WorkflowQueue>(
              itm =>
              {

                  itm.ToTable("IN_WF_QUEUE");
                  itm.Property(o => o.Id).HasColumnName("QUEUE_ID");
                  itm.Property(o => o.Name).HasColumnName("QUEUE_NAME");
                  itm.Property(o => o.ContainItems).HasColumnName("CONTAINS_ITEMS");
                  itm.Property(o => o.ProcessId).HasColumnName("PROCESS_ID");

              }
              );
            builder.Entity<Property>(
              prp =>
              {

                  prp.ToTable("IN_INSTANCE_PROP");
                  prp.Property(o => o.Id).HasColumnName("PROP_ID");
                  prp.Property(o => o.Value).HasColumnName("TIME_VAL");
                  prp.Property(o => o.InstanceId).HasColumnName("INSTANCE_ID");

              }
              );
           

        }
    }
}