-- with Ada.Text_IO, Ada.Integer_Text_IO;
-- use Ada.Text_IO, Ada.Integer_Text_IO;

procedure LinkList is
	b : float;
	type CHAR_REC;
	type CHAR_REC_POINT is access CHAR_REC;
	type CHAR_REC is record
		One_Letter : integer;
		Next_Rec   : CHAR_REC_POINT;
	end record;
	procedure Traverse_List (Starting_Point : CHAR_REC_POINT) is
		a : integer;
		Temp : CHAR_REC_POINT;
	begin
		a := 4;
		-- Put("In traverse routine.  --->");
		Temp := Starting_Point;
		if Temp = null then
			print_int(5);
		else
			a := 5;
			while Temp != null loop
				print_int (6);
				print_int (Temp.One_Letter);
				Temp := Temp.Next_Rec;
			end loop;
			print_int (7);
		end if;
		a := 89;
	end;
	procedure main is
		LL : CHAR_REC_POINT;
		z : integer;
	begin
		z := 5;
		LL := new CHAR_REC;
		Traverse_List (LL);
	end;
begin
	main;
end;