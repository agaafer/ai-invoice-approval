USE [AlaaTest]
GO
/****** Object:  UserDefinedFunction [dbo].[fn_getName]    Script Date: 9/10/2026 4:01:32 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		<Author,,Name>
-- Create date: <Create Date, ,>
-- Description:	<Description, ,>
-- =============================================
CREATE FUNCTION [dbo].[fn_getName] 
(
	-- Add the parameters for the function here
	@DocumentId nvarchar(50)
)
RETURNS nvarchar(50)
AS
BEGIN
	-- Declare the return variable here
	DECLARE @result as nvarchar(50)

	-- Add the T-SQL statements to compute the return value here
	 Select @result= JSON_VALUE(PredictionResult, '$.prediction.name') from BatchPredection
	where DocumentId = @DocumentId
	

	-- Return the result of the function
	RETURN @result

END
GO
/****** Object:  UserDefinedFunction [dbo].[fn_getPercent]    Script Date: 9/10/2026 4:01:32 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		<Author,,Name>
-- Create date: <Create Date, ,>
-- Description:	<Description, ,>
-- =============================================
CREATE FUNCTION [dbo].[fn_getPercent] 
(
	-- Add the parameters for the function here
	@DocumentId nvarchar(50)
)
RETURNS nvarchar(50)
AS
BEGIN
	-- Declare the return variable here
	DECLARE @result as nvarchar(50)

	-- Add the T-SQL statements to compute the return value here
	 Select @result= JSON_VALUE(PredictionResult, '$.prediction.percent') from BatchPredection
	where DocumentId = @DocumentId
	

	-- Return the result of the function
	RETURN @result

END
GO
/****** Object:  Table [dbo].[BatchPredection]    Script Date: 9/10/2026 4:01:32 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BatchPredection](
	[Id] [bigint] IDENTITY(1,1) NOT NULL,
	[DocumentId] [nvarchar](50) NULL,
	[PredictionResult] [nvarchar](4000) NULL,
	[Percent]  AS ([dbo].[fn_getPercent]([DocumentId])),
	[Name]  AS ([dbo].[fn_getName]([DocumentId])),
 CONSTRAINT [PK_Predection] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BatchPredictionNotes]    Script Date: 9/10/2026 4:01:32 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BatchPredictionNotes](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[DocumentId] [nvarchar](50) NULL,
	[InvoiceNumber] [nvarchar](50) NULL,
	[Notes] [nvarchar](1000) NULL,
 CONSTRAINT [PK_BatchPredictionNotes] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
