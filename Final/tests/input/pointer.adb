with Ada.Text_IO, Ada.Integer_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO;

procedure LinkList is
	a : Integer;
	type CHAR_REC;
	type CHAR_REC_POINT is access CHAR_REC;
	type CHAR_REC is record
		One_Letter : Integer;
		Next_Rec   : CHAR_REC_POINT;
	end record;
begin
	a := 5;
end;