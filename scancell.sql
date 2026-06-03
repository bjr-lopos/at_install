-- Candidate UWB links for curateCells' broad scan.
-- While this table is non-empty, planActions() calls uwbScanCells() each hyperframe,
-- scheduling scenario-13 (Uwb) rounds for these (core,edge) pairs in free SFs (guarded),
-- in parallel with normal localization. curateCells fills it, waits, reads uwbstat, empties it.
CREATE TABLE IF NOT EXISTS scancell (
  core INT NOT NULL,
  edge INT NOT NULL,
  PRIMARY KEY (core, edge)
);
