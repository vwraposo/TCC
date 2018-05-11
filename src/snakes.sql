-- Creating first tables
CREATE TABLE snakes (
  sn_sp varchar(100) not NULL, 
  sn_ge varchar(100) not NULL,
  CONSTRAINT pk_sn PRIMARY KEY (sn_sp)
);

CREATE TABLE mtDNAs (
  mt_acc varchar(100) not NULL, 
  mt_desc text, 
  mt_seq text, 
  mt_alias varchar(100), 
  sn_sp varchar(100), 
  CONSTRAINT pk_mt PRIMARY KEY (mt_acc), 
  CONSTRAINT fk_sn FOREIGN KEY (sn_sp)
    REFERENCES snakes(sn_sp)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- Inserting snakes
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('moojeni', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('jararacussu', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('neuwiedi', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('erythromelas', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('insularis', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('jararaca', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('cotiara', 'Bothrops');


-- Creating Protein and Peptide:

CREATE TABLE peptides (
  pep_seq varchar(100) not NULL, 
  CONSTRAINT pk_pep PRIMARY KEY (pep_seq)
);

CREATE TABLE proteins (
  pr_acc varchar(100), 
  pr_toxclass varchar(100), 
  CONSTRAINT pk_pr PRIMARY KEY (pr_acc)
);

CREATE TABLE pep_pr (
  pep_seq varchar(100), 
  pr_acc varchar(100),
  CONSTRAINT fk_pr FOREIGN KEY (pr_acc)
    REFERENCES proteins(pr_acc)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_pep FOREIGN KEY (pep_seq)
    REFERENCES peptides(pep_seq)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABlE pr_sn (
  sn_sp varchar(100), 
  pr_acc varchar(100),
  CONSTRAINT fk_pr FOREIGN KEY (pr_acc)
    REFERENCES proteins(pr_acc)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_sn FOREIGN KEY (sn_sp)
    REFERENCES snakes(sn_sp)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE pep_sn (
  pep_seq varchar(100), 
  sn_sp varchar(100),
  CONSTRAINT fk_sn FOREIGN KEY (sn_sp)
    REFERENCES snakes(sn_sp)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_pep FOREIGN KEY (pep_seq)
    REFERENCES peptides(pep_seq)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
