/* ============================================================
   ImageNow API Database Schema
   Schema: inuser
   ============================================================ */

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

/* ============================================================
   Create Schema
   ============================================================ */

IF NOT EXISTS
(
    SELECT 1
    FROM sys.schemas
    WHERE name = N'inuser'
)
BEGIN
    EXEC(N'CREATE SCHEMA [inuser]');
END
GO


/* ============================================================
   IN_INSTANCE
   ============================================================ */

IF OBJECT_ID(N'[inuser].[IN_INSTANCE]', N'U') IS NULL
BEGIN

    CREATE TABLE [inuser].[IN_INSTANCE]
    (
        [INSTANCE_ID]    nvarchar(450) NOT NULL,
        [CREATION_TIME]  datetime2 NULL,
        [MOD_TIME]       datetime2 NULL,

        CONSTRAINT [PK_IN_INSTANCE]
            PRIMARY KEY CLUSTERED ([INSTANCE_ID])
    );

END
GO


/* ============================================================
   IN_WF_QUEUE
   ============================================================ */

IF OBJECT_ID(N'[inuser].[IN_WF_QUEUE]', N'U') IS NULL
BEGIN

    CREATE TABLE [inuser].[IN_WF_QUEUE]
    (
        [QUEUE_ID]       nvarchar(450) NOT NULL,
        [QUEUE_NAME]     nvarchar(max) NULL,
        [CONTAINS_ITEMS] int NOT NULL,
        [PROCESS_ID]     nvarchar(max) NULL,

        CONSTRAINT [PK_IN_WF_QUEUE]
            PRIMARY KEY CLUSTERED ([QUEUE_ID])
    );

END
GO


/* ============================================================
   IN_DOC
   ============================================================ */

IF OBJECT_ID(N'[inuser].[IN_DOC]', N'U') IS NULL
BEGIN

    CREATE TABLE [inuser].[IN_DOC]
    (
        [DOC_ID]         nvarchar(450) NOT NULL,
        [INSTANCE_ID]    nvarchar(450) NULL,
        [FOLDER]         nvarchar(max) NULL,
        [TAB]            nvarchar(max) NULL,
        [F3]             nvarchar(max) NULL,
        [DOC_TYPE_ID]    nvarchar(max) NULL,

        CONSTRAINT [PK_IN_DOC]
            PRIMARY KEY CLUSTERED ([DOC_ID]),

        CONSTRAINT [FK_IN_DOC_IN_INSTANCE]
            FOREIGN KEY ([INSTANCE_ID])
            REFERENCES [inuser].[IN_INSTANCE] ([INSTANCE_ID])
    );

END
GO


/* ============================================================
   IN_WF_ITEM
   ============================================================ */

IF OBJECT_ID(N'[inuser].[IN_WF_ITEM]', N'U') IS NULL
BEGIN

    CREATE TABLE [inuser].[IN_WF_ITEM]
    (
        [ITEM_ID]          nvarchar(450) NOT NULL,
        [QUEUE_ID]         nvarchar(450) NULL,
        [INSTANCE_ID]      nvarchar(450) NULL,
        [QUEUE_START_TIME] datetime2 NULL,

        CONSTRAINT [PK_IN_WF_ITEM]
            PRIMARY KEY CLUSTERED ([ITEM_ID]),

        CONSTRAINT [FK_IN_WF_ITEM_IN_WF_QUEUE]
            FOREIGN KEY ([QUEUE_ID])
            REFERENCES [inuser].[IN_WF_QUEUE] ([QUEUE_ID]),

        CONSTRAINT [FK_IN_WF_ITEM_IN_INSTANCE]
            FOREIGN KEY ([INSTANCE_ID])
            REFERENCES [inuser].[IN_INSTANCE] ([INSTANCE_ID])
    );

END
GO


/* ============================================================
   IN_INSTANCE_PROP
   ============================================================ */

IF OBJECT_ID(N'[inuser].[IN_INSTANCE_PROP]', N'U') IS NULL
BEGIN

    CREATE TABLE [inuser].[IN_INSTANCE_PROP]
    (
        [PROP_ID]       nvarchar(450) NOT NULL,
        [TIME_VAL]      datetime2 NULL,
        [INSTANCE_ID]   nvarchar(450) NULL,

        CONSTRAINT [PK_IN_INSTANCE_PROP]
            PRIMARY KEY CLUSTERED ([PROP_ID]),

        CONSTRAINT [FK_IN_INSTANCE_PROP_IN_INSTANCE]
            FOREIGN KEY ([INSTANCE_ID])
            REFERENCES [inuser].[IN_INSTANCE] ([INSTANCE_ID])
    );

END
GO


/* ============================================================
   Indexes
   ============================================================ */

/* Document -> Instance */
IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_IN_DOC_INSTANCE_ID'
      AND object_id = OBJECT_ID(N'[inuser].[IN_DOC]')
)
BEGIN
    CREATE INDEX [IX_IN_DOC_INSTANCE_ID]
        ON [inuser].[IN_DOC] ([INSTANCE_ID]);
END
GO


/* Workflow Item -> Queue */
IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_IN_WF_ITEM_QUEUE_ID'
      AND object_id = OBJECT_ID(N'[inuser].[IN_WF_ITEM]')
)
BEGIN
    CREATE INDEX [IX_IN_WF_ITEM_QUEUE_ID]
        ON [inuser].[IN_WF_ITEM] ([QUEUE_ID]);
END
GO


/* Workflow Item -> Instance */
IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_IN_WF_ITEM_INSTANCE_ID'
      AND object_id = OBJECT_ID(N'[inuser].[IN_WF_ITEM]')
)
BEGIN
    CREATE INDEX [IX_IN_WF_ITEM_INSTANCE_ID]
        ON [inuser].[IN_WF_ITEM] ([INSTANCE_ID]);
END
GO


/* Instance Property -> Instance */
IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_IN_INSTANCE_PROP_INSTANCE_ID'
      AND object_id = OBJECT_ID(N'[inuser].[IN_INSTANCE_PROP]')
)
BEGIN
    CREATE INDEX [IX_IN_INSTANCE_PROP_INSTANCE_ID]
        ON [inuser].[IN_INSTANCE_PROP] ([INSTANCE_ID]);
END
GO