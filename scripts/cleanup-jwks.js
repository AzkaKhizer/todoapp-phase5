/**
 * Script to clean up JWKS tables from the database.
 * Run with: node scripts/cleanup-jwks.js
 */

const { Pool } = require('pg');

async function cleanupJWKS() {
  // Note: DATABASE_URL should be set as environment variable

  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.DATABASE_URL?.includes('neon')
      ? { rejectUnauthorized: false }
      : undefined,
  });

  try {
    console.log('Checking for JWKS tables...');

    // Check if jwk table exists
    const tableCheck = await pool.query(`
      SELECT tablename
      FROM pg_catalog.pg_tables
      WHERE schemaname = 'public'
      AND tablename LIKE '%jwk%'
    `);

    if (tableCheck.rows.length > 0) {
      console.log('Found JWKS tables:', tableCheck.rows.map(r => r.tablename));

      for (const row of tableCheck.rows) {
        console.log(`Dropping table: ${row.tablename}`);
        await pool.query(`DROP TABLE IF EXISTS "${row.tablename}" CASCADE`);
      }

      console.log('JWKS tables removed successfully.');
    } else {
      console.log('No JWKS tables found in database.');
    }

    // List all remaining tables
    const allTables = await pool.query(`
      SELECT tablename
      FROM pg_catalog.pg_tables
      WHERE schemaname = 'public'
      ORDER BY tablename
    `);

    console.log('\nRemaining tables:', allTables.rows.map(r => r.tablename).join(', '));

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

cleanupJWKS();
