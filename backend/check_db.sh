#!/bin/bash
psql postgresql://postgres:Postgrespwd12345.@localhost:5432/tender_db -c "\dt"
echo "---"
psql postgresql://postgres:Postgrespwd12345.@localhost:5432/tender_db -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
