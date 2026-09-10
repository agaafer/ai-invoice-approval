using Microsoft.EntityFrameworkCore;
using Reliance.ImageNow.API.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Reliance.ImageNow.API.Data
{
    public class PredictionDbContext : DbContext
    {
        public DbSet<BatchPredection> BatchPredections { get; set; }
        public DbSet<BatchPredictionNotes> BatchPredictionNotes { get; set; }

        public PredictionDbContext(DbContextOptions<PredictionDbContext> options) : base(options) { }

        protected override void OnModelCreating(ModelBuilder builder)
        {
            base.OnModelCreating(builder);
            builder.Entity<BatchPredection>(
               doc =>
               {

                   doc.ToTable("BatchPredection");
               }
               );
            builder.Entity<BatchPredictionNotes>(
                doc =>
                {

                    doc.ToTable("BatchPredictionNotes");
                }
                );



        }
    }
}